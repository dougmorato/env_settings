# This file is part of hgreview.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.

import os
import re
import sys
from hashlib import md5

from mercurial import hg
from mercurial import commands, cmdutil, patch, mdiff, copies, node

from rietveld import (GetEmail, GetRpcServer, CheckReviewer, MAX_UPLOAD_SIZE,
    EncodeMultipartFormData, UploadSeparatePatches, UploadBaseFiles)

def review(ui, repo, *args, **opts):
    node1, node2 = cmdutil.revpair(repo, opts['rev'])
    modified, added, removed, deleted, unknown, ignored, clean = \
            repo.status(node1, node2, unknown=True)
    if unknown:
        ui.status('The following files are not added to version control:', '\n\n')
        for filename in unknown:
            ui.status(filename, '\n')
        cont = ui.prompt("\nAre you sure to continue? (y/N) ", 'N')
        if cont.lower() not in ('y', 'yes'):
            sys.exit(0)

    opts['git'] = True
    difffiles = patch.diff(repo, node1, node2, opts=mdiff.diffopts(git=True))
    svndiff, filecount = [], 0
    for diffedfile in difffiles:
        for line in diffedfile.split('\n'):
            m = re.match(patch.gitre, line)
            if m:
                # Modify line to make it look like as it comes from svn diff.
                # With this modification no changes on the server side are required
                # to make upload.py work with Mercurial repos.
                # NOTE: for proper handling of moved/copied files, we have to use
                # the second filename.
                filename = m.group(2)
                svndiff.append("Index: %s" % filename)
                svndiff.append("=" * 67)
                filecount += 1
            else:
                svndiff.append(line)
    if not filecount:
        # No valid patches in hg diff
        sys.exit(1)
    data = '\n'.join(svndiff) + '\n'

    base_rev = repo[node1]
    current_rev = repo[node2]
    null_rev = repo[node.nullid]
    files = {}

    # getting informations about copied/moved files
    copymove_info = copies.copies(repo, base_rev, current_rev, null_rev)[0]
    for newname, oldname in copymove_info.items():
        oldcontent = base_rev[oldname].data()
        newcontent = current_rev[newname].data()
        is_binary = "\0" in oldcontent or "\0" in newcontent
        files[newname] = (oldcontent, newcontent, is_binary, 'M')

    # modified files
    for filename in cmdutil.matchfiles(repo, modified):
        oldcontent = base_rev[filename].data()
        newcontent = current_rev[filename].data()
        is_binary = "\0" in oldcontent or "\0" in newcontent
        files[filename] = (oldcontent, newcontent, is_binary, 'M')

    # added files
    for filename in cmdutil.matchfiles(repo, added):
        oldcontent = ''
        newcontent = current_rev[filename].data()
        is_binary = "\0" in newcontent
        files[filename] = (oldcontent, newcontent, is_binary, 'A')

    # removed files
    for filename in cmdutil.matchfiles(repo, removed):
        if filename in copymove_info.values():
            # file has been moved or copied
            continue
        oldcontent = base_rev[filename].data()
        newcontent = ''
        is_binary = "\0" in oldcontent
        files[filename] = (oldcontent, newcontent, is_binary, 'R')

    issue_file = os.path.join(repo.root, '.hg', 'review_id')
    if opts['issue']:
        if not os.path.isfile(issue_file):
            open(issue_file, 'w').write(opts['issue'])
            ui.message('Creating %s file' % issue_file, '\n')
        prompt = "Message describing this patch set: "
        issue_id = opts['issue']
    elif os.path.isfile(issue_file):
        prompt = "Message describing this patch set: "
        issue_id = open(issue_file, 'r').read().strip()
    else:
        prompt = "New issue subject: "
        issue_id = None
    message = ui.prompt(prompt, '')
    if not message:
        sys.exit(1)

    server = ui.config('review', 'server',
        default='http://codereview.appspot.com')
    username = ui.config('review', 'username')
    if not username:
        username = rietveld.GetEmail(ui)
        ui.setconfig('review', 'username', username)
    host_header = ui.config('review', 'host_header')
    account_type = ui.config('review', 'account_type', 'GOOGLE')
    rpc_server = GetRpcServer(server, username, host_header, True, account_type,
        ui)
    form_fields = [('subject', message)]
    if issue_id:
        form_fields.append(('issue', issue_id))
    if username:
        form_fields.append(('user', username))
    if opts['reviewers']:
        for reviewer in opts['reviewers']:
            CheckReviewer(reviewer)
        form_fields.append(('reviewers', ','.join(opts['reviewers'])))
    cc_header = ui.config('review', 'cc_header')
    if cc_header:
        for cc in cc_header.split(','):
            CheckReviewer(cc)
        form_fields.append(("cc", cc_header))

    # Send a hash of all the base file so the server can determine if a copy
    # already exists in an earlier patchset.
    base_hashes = []
    for filename, info in files.iteritems():
        if info[0] is not None:
            checksum = md5(info[0]).hexdigest()
            base_hashes.append('%s:%s' % (checksum, filename))
    form_fields.append(('base_hashes', '|'.join(base_hashes)))

    # I choose to upload content by default see upload.py for other options
    form_fields.append(('content_upload', '1'))
    if len(data) > MAX_UPLOAD_SIZE:
        uploaded_diff_file = []
        form_fields.append(('separate_patches', '1'))
    else:
        uploaded_diff_file = [('data', 'data.diff', data)]
    ctype, body = EncodeMultipartFormData(form_fields, uploaded_diff_file)
    response_body = rpc_server.Send('/upload', body, content_type=ctype)

    lines = response_body.splitlines()
    if len(lines) > 1:
        msg = lines[0]
        patchset = lines[1].strip()
        patches = [x.split(' ', 1) for x in lines[2:]]
    else:
        msg = response_body
    ui.status(msg, '\n')
    if not (response_body.startswith('Issue created.')
            or response_body.startswith('Issue updated.')):
        sys.exit(0)
    issue_id = msg[msg.rfind('/')+1:]
    open(issue_file, 'w').write(issue_id)
    if not uploaded_diff_file:
        patches = UploadSeparatePatches(issue_id, rpc_server, patchset, data, ui)
    UploadBaseFiles(issue_id, rpc_server, patches, patchset, username, files, ui)
    if opts['send_email'] or ui.configbool('review', 'send_email'):
        rpc_server.Send('/%s/mail' % issue_id, payload='')

# Add option for description, private
cmdtable = {
    'review': (review, [
        ('r', 'reviewers', [], 'Add reviewers'),
        ('i', 'issue', '', 'Issue number. Defaults to new issue'),
        ('', 'rev', '', 'Revision number to diff against'),
        ('', 'send_email', None, 'Send notification email to reviewers'),
    ], "hg review [options]"),
}
