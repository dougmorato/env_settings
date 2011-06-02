# This file is part of hgreview.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.
# This file contains code from upload.py python script to upload on rietveld
# servers licensed under the apache license v2.0 (c) Google Inc.
import os
import urllib
import urllib2
import cookielib
import logging
import mimetypes
import socket
from hashlib import md5

AUTH_ACCOUNT_TYPE = "GOOGLE"
MAX_UPLOAD_SIZE = 900 * 1024

def UploadBaseFiles(issue, rpc_server, patch_list, patchset, username, files, ui):
    """Uploads the base files (and if necessary, the current ones as well)."""

    def UploadFile(filename, file_id, content, is_binary, status, is_base):
        """Uploads a file to the server."""
        file_too_large = False
        if is_base:
            type = "base"
        else:
            type = "current"
        if len(content) > MAX_UPLOAD_SIZE:
            ui.status("Not uploading the %s file for %s because it's too large."
                % (type, filename))
            file_too_large = True
            content = ""
        checksum = md5(content).hexdigest()
        if not file_too_large:
            ui.status("Uploading %s file for %s" % (type, filename), '\n')
        url = "/%d/upload_content/%d/%d" % (int(issue), int(patchset), file_id)
        form_fields = [
            ("filename", filename),
            ("status", status),
            ("checksum", checksum),
            ("is_binary", str(is_binary)),
            ("is_current", str(not is_base)),
        ]
        if file_too_large:
            form_fields.append(("file_too_large", "1"))
        form_fields.append(("user", username))
        ctype, body = EncodeMultipartFormData(form_fields,
            [("data", filename, content)])
        response_body = rpc_server.Send(url, body, content_type=ctype)
        if not response_body.startswith("OK"):
            ui.status('  --> %s' % response_body, '\n')
            sys.exit(1)

    patches = dict()
    [patches.setdefault(v, k) for k, v in patch_list]
    for filename in patches.keys():
        base_content, new_content, is_binary, status = files[filename]
        file_id_str = patches.get(filename)
        if file_id_str.find("nobase") != -1:
            base_content = None
            file_id_str = file_id_str[file_id_str.rfind("_") + 1:]
        file_id = int(file_id_str)
        if base_content != None:
            UploadFile(filename, file_id, base_content, is_binary, status, True)
        if new_content != None:
            UploadFile(filename, file_id, new_content, is_binary, status, False)

def UploadSeparatePatches(issue, rpc_server, patchset, data, ui):
    """Uploads a separate patch for each file in the diff output.

    Returns a list of [patch_key, filename] for each file.
    """
    patches = SplitPatch(data)
    rv = []
    for patch in patches:
        if len(patch[1]) > MAX_UPLOAD_SIZE:
            ui.status('Not uploading the patch for %s because'
                ' the file is too large' % patch[0])
            continue
        form_fields = [("filename", patch[0])]
        form_fields.append(("content_upload", "1"))
        files = [("data", "data.diff", patch[1])]
        ctype, body = EncodeMultipartFormData(form_fields, files)
        url = "/%d/upload_patch/%d" % (int(issue), int(patchset))
        ui.status("Uploading patch for %s" % patch[0], '\n')
        response_body = rpc_server.Send(url, body, content_type=ctype)
        lines = response_body.splitlines()
        if not lines or lines[0] != "OK":
            ui.status(' --> %s' % response_body, '\n')
            sys.exit(1)
        rv.append([lines[1], patch[0]])
    return rv

def GetContentType(filename):
  """Helper to guess the content-type from the filename."""
  return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def EncodeMultipartFormData(fields, files):
    """Encode form fields for multipart/form-data.

    Args:
      fields: A sequence of (name, value) elements for regular form fields.
      files: A sequence of (name, filename, value) elements for data to be
             uploaded as files.
    Returns:
      (content_type, body) ready for httplib.HTTP instance.

    Source:
      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
    """
    BOUNDARY = '-M-A-G-I-C---B-O-U-N-D-A-R-Y-'
    CRLF = '\r\n'
    lines = []
    for (key, value) in fields:
        lines.append('--' + BOUNDARY)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        lines.append(value)
    for (key, filename, value) in files:
        lines.append('--' + BOUNDARY)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' %
            (key, filename))
        lines.append('Content-Type: %s' % GetContentType(filename))
        lines.append('')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        lines.append(value)
    lines.append('--' + BOUNDARY + '--')
    lines.append('')
    body = CRLF.join(lines)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def CheckReviewer(reviewer):
    """Validate a reviewer -- either a nickname or an email addres.

    Args:
      reviewer: A nickname or an email address.

    Calls ErrorExit() if it is an invalid email address.
    """
    if "@" not in reviewer:
        return  # Assume nickname
    parts = reviewer.split("@")
    if len(parts) > 2:
        ErrorExit("Invalid email address: %r" % reviewer)
    assert len(parts) == 2
    if "." not in parts[1]:
        ErrorExit("Invalid email address: %r" % reviewer)

def GetEmail(ui):
    """Prompts the user for their email address and returns it.

    The last used email address is saved to a file and offered up as a suggestion
    to the user. If the user presses enter without typing in anything the last
    used email address is used. If the user enters a new address, it is saved
    for next time we prompt.

    """
    prompt = "Email (login for uploading)"
    last_email_file_name = os.path.expanduser("~/.last_codereview_email_address")
    last_email = ""
    if os.path.exists(last_email_file_name):
        try:
            last_email_file = open(last_email_file_name, "r")
            last_email = last_email_file.readline().strip("\n")
            last_email_file.close()
            prompt += " [%s]" % last_email
        except IOError, e:
            pass
    email = ui.prompt(prompt + ': ', last_email)
    if email:
        try:
            last_email_file = open(last_email_file_name, "w")
            last_email_file.write(email)
            last_email_file.close()
        except IOError, e:
            pass
    else:
        email = last_email
    return email

def GetRpcServer(server, email=None, host_override=None, save_cookies=True,
                 account_type=AUTH_ACCOUNT_TYPE, ui=None):
    """Returns an instance of an AbstractRpcServer.

    Args:
      server: String containing the review server URL.
      email: String containing user's email address.
      host_override: If not None, string containing an alternate hostname to use
        in the host header.
      save_cookies: Whether authentication cookies should be saved to disk.
      account_type: Account type for authentication, either 'GOOGLE'
        or 'HOSTED'. Defaults to AUTH_ACCOUNT_TYPE.

    Returns:
      A new AbstractRpcServer, on which RPC calls can be made.
    """

    rpc_server_class = HttpRpcServer

    # If this is the dev_appserver, use fake authentication.
    host = (host_override or server).lower()
    if host == "localhost" or host.startswith("localhost:"):
        if email is None:
          email = "test@example.com"
          logging.info("Using debug user %s.  Override with --email" % email)
        server = rpc_server_class(
            server,
            lambda: (email, "password"),
            host_override=host_override,
            extra_headers={"Cookie":
                'dev_appserver_login="%s:False"' % email},
            save_cookies=save_cookies,
            account_type=account_type, ui=ui)
        # Don't try to talk to ClientLogin.
        server.authenticated = True
        return server

    def GetUserCredentials():
        """Prompts the user for a username and password."""
        # Create a local alias to the email variable to avoid Python's crazy
        # scoping rules.
        local_email = email
        if local_email is None:
            local_email = GetEmail("Email (login for uploading to %s)" % server)
        password = ui.getpass('Password for %s:' % local_email, None)
        return (local_email, password)

    return rpc_server_class(server,
        GetUserCredentials, host_override=host_override,
        save_cookies=save_cookies, ui=ui)


class ClientLoginError(urllib2.HTTPError):
  """Raised to indicate there was an error authenticating with ClientLogin."""

  def __init__(self, url, code, msg, headers, args):
    urllib2.HTTPError.__init__(self, url, code, msg, headers, None)
    self.args = args
    self.reason = args["Error"]


class AbstractRpcServer(object):
    """Provides a common interface for a simple RPC server."""

    def __init__(self, host, auth_function, host_override=None, extra_headers={},
                 save_cookies=False, account_type=AUTH_ACCOUNT_TYPE, ui=None):
        """Creates a new HttpRpcServer.

        Args:
          host: The host to send requests to.
          auth_function: A function that takes no arguments and returns an
            (email, password) tuple when called. Will be called if authentication
            is required.
          host_override: The host header to send to the server (defaults to host).
          extra_headers: A dict of extra headers to append to every request.
          save_cookies: If True, save the authentication cookies to local disk.
            If False, use an in-memory cookiejar instead.  Subclasses must
            implement this functionality.  Defaults to False.
          account_type: Account type used for authentication. Defaults to
            AUTH_ACCOUNT_TYPE.
        """
        self.host = host
        if (not self.host.startswith("http://") and
                not self.host.startswith("https://")):
            self.host = "http://" + self.host
        self.host_override = host_override
        self.auth_function = auth_function
        self.authenticated = False
        self.extra_headers = extra_headers
        self.save_cookies = save_cookies
        self.account_type = account_type
        self.opener = self._GetOpener()
        self.ui = ui
        if self.host_override:
            logging.info("Server: %s; Host: %s", self.host, self.host_override)
        else:
            logging.info("Server: %s", self.host)

    def _GetOpener(self):
        """Returns an OpenerDirector for making HTTP requests.

        Returns:
          A urllib2.OpenerDirector object.
        """
        raise NotImplementedError()

    def _CreateRequest(self, url, data=None):
        """Creates a new urllib request."""
        logging.debug("Creating request for: '%s' with payload:\n%s", url, data)
        req = urllib2.Request(url, data=data)
        if self.host_override:
            req.add_header("Host", self.host_override)
        for key, value in self.extra_headers.iteritems():
            req.add_header(key, value)
        return req

    def _GetAuthToken(self, email, password):
        """Uses ClientLogin to authenticate the user, returning an auth token.

        Args:
          email:    The user's email address
          password: The user's password

        Raises:
          ClientLoginError: If there was an error authenticating with ClientLogin.
          HTTPError: If there was some other form of HTTP error.

        Returns:
          The authentication token returned by ClientLogin.
        """
        account_type = self.account_type
        if self.host.endswith(".google.com"):
            # Needed for use inside Google.
            account_type = "HOSTED"
        req = self._CreateRequest(
            url="https://www.google.com/accounts/ClientLogin",
            data=urllib.urlencode({
                "Email": email,
                "Passwd": password,
                "service": "ah",
                "source": "rietveld-codereview-upload",
                "accountType": account_type,
            }),
        )
        try:
            response = self.opener.open(req)
            response_body = response.read()
            response_dict = dict(x.split("=")
                for x in response_body.split("\n") if x)
            return response_dict["Auth"]
        except urllib2.HTTPError, e:
            if e.code == 403:
                body = e.read()
                response_dict = dict(x.split("=", 1)
                    for x in body.split("\n") if x)
                raise ClientLoginError(req.get_full_url(), e.code, e.msg,
                    e.headers, response_dict)
            else:
                raise

    def _GetAuthCookie(self, auth_token):
        """Fetches authentication cookies for an authentication token.

        Args:
          auth_token: The authentication token returned by ClientLogin.

        Raises:
          HTTPError: If there was an error fetching the authentication cookies.
        """
        # This is a dummy value to allow us to identify when we're successful.
        continue_location = "http://localhost/"
        args = {"continue": continue_location, "auth": auth_token}
        req = self._CreateRequest("%s/_ah/login?%s" %
            (self.host, urllib.urlencode(args)))
        try:
            response = self.opener.open(req)
        except urllib2.HTTPError, e:
            response = e
        if (response.code != 302 or
                response.info()["location"] != continue_location):
          raise urllib2.HTTPError(req.get_full_url(), response.code,
              response.msg, response.headers, response.fp)
        self.authenticated = True

    def _Authenticate(self):
        """Authenticates the user.

        The authentication process works as follows:
         1) We get a username and password from the user
         2) We use ClientLogin to obtain an AUTH token for the user
            (see http://code.google.com/apis/accounts/AuthForInstalledApps.html).
         3) We pass the auth token to /_ah/login on the server to obtain an
            authentication cookie. If login was successful, it tries to redirect
            us to the URL we provided.

        If we attempt to access the upload API without first obtaining an
        authentication cookie, it returns a 401 response (or a 302) and
        directs us to authenticate ourselves with ClientLogin.
        """
        for i in range(3):
            credentials = self.auth_function()
            try:
                auth_token = self._GetAuthToken(credentials[0], credentials[1])
            except ClientLoginError, e:
                if e.reason == "BadAuthentication":
                    self.ui.status("Invalid username or password.", '\n')
                    continue
                if e.reason == "CaptchaRequired":
                    self.ui.status(
                        "Please go to\n"
                        "https://www.google.com/accounts/DisplayUnlockCaptcha\n"
                        "and verify you are a human.  Then try again.\n"
                        "If you are using a Google Apps account the URL is:\n"
                        "https://www.google.com/a/yourdomain.com/UnlockCaptcha\n")
                    break
                if e.reason == "NotVerified":
                    self.ui.status("Account not verified.", '\n')
                    break
                if e.reason == "TermsNotAgreed":
                    self.ui.status("User has not agreed to TOS.", '\n')
                    break
                if e.reason == "AccountDeleted":
                    self.ui.status("The user account has been deleted.", '\n')
                    break
                if e.reason == "AccountDisabled":
                    self.ui.status("The user account has been disabled.", '\n')
                    break
                if e.reason == "ServiceDisabled":
                    self.ui.status("The user's access to the service has been ",
                        "disabled.\n")
                    break
                if e.reason == "ServiceUnavailable":
                    self.ui.status("The service is not available; try again"
                        " later.\n")
                    break
                raise
            self._GetAuthCookie(auth_token)
            break

    def Send(self, request_path, payload=None,
            content_type="application/octet-stream", timeout=None,
            extra_headers=None, **kwargs):
        """Sends an RPC and returns the response.

        Args:
          request_path: The path to send the request to, eg /api/appversion/create.
          payload: The body of the request, or None to send an empty request.
          content_type: The Content-Type header to use.
          timeout: timeout in seconds; default None i.e. no timeout.
            (Note: for large requests on OS X, the timeout doesn't work right.)
          extra_headers: Dict containing additional HTTP headers that should be
            included in the request (string header names mapped to their values),
            or None to not include any additional headers.
          kwargs: Any keyword arguments are converted into query string parameters.

        Returns:
          The response body, as a string.
        """
        # TODO: Don't require authentication.  Let the server say
        # whether it is necessary.
        if not self.authenticated:
            self._Authenticate()

        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
            tries = 0
            while True:
                tries += 1
                args = dict(kwargs)
                url = "%s%s" % (self.host, request_path)
                if args:
                    url += "?" + urllib.urlencode(args)
                req = self._CreateRequest(url=url, data=payload)
                req.add_header("Content-Type", content_type)
                if extra_headers:
                    for header, value in extra_headers.items():
                        req.add_header(header, value)
                try:
                    f = self.opener.open(req)
                    response = f.read()
                    f.close()
                    return response
                except urllib2.HTTPError, e:
                    if tries > 3:
                        raise
                    elif e.code == 401 or e.code == 302:
                        self._Authenticate()
                    else:
                        raise
        finally:
            socket.setdefaulttimeout(old_timeout)


class HttpRpcServer(AbstractRpcServer):
    """Provides a simplified RPC-style interface for HTTP requests."""

    def _Authenticate(self):
      """Save the cookie jar after authentication."""
      super(HttpRpcServer, self)._Authenticate()
      if self.save_cookies:
          self.cookie_jar.save()

    def _GetOpener(self):
      """Returns an OpenerDirector that supports cookies and ignores redirects.

      Returns:
        A urllib2.OpenerDirector object.
      """
      opener = urllib2.OpenerDirector()
      opener.add_handler(urllib2.ProxyHandler())
      opener.add_handler(urllib2.UnknownHandler())
      opener.add_handler(urllib2.HTTPHandler())
      opener.add_handler(urllib2.HTTPDefaultErrorHandler())
      opener.add_handler(urllib2.HTTPSHandler())
      opener.add_handler(urllib2.HTTPErrorProcessor())
      if self.save_cookies:
          self.cookie_file = os.path.expanduser("~/.codereview_upload_cookies")
          self.cookie_jar = cookielib.MozillaCookieJar(self.cookie_file)
          if os.path.exists(self.cookie_file):
              try:
                  self.cookie_jar.load()
                  self.authenticated = True
              except (cookielib.LoadError, IOError):
                  # Failed to load cookies - just ignore them.
                  pass
          else:
              # Create an empty cookie file with mode 600
              fd = os.open(self.cookie_file, os.O_CREAT, 0600)
              os.close(fd)
          # Always chmod the cookie file
          os.chmod(self.cookie_file, 0600)
      else:
          # Don't save cookies across runs of update.py.
          self.cookie_jar = cookielib.CookieJar()
      opener.add_handler(urllib2.HTTPCookieProcessor(self.cookie_jar))
      return opener


