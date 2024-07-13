import socket
import ssl
import gzip
import io

class URL: 
  def __init__(self, url):

    self.viewSource = False
    if url.startswith("view-source:"):
      self.viewSource = True
      _, url = url.split(":", 1) 
    if "://" in url:
      self.scheme, url = url.split("://", 1)
    else:
      self.scheme, url = url.split(":", 1)
    assert self.scheme in ["http", "https", "file", "data", "view-source"]
    
    if self.scheme == "http":
      self.port = 80
    if self.scheme == "https":
      self.port = 443
    if self.scheme == "file":
      self.port = 445
    if "/" not in url:
      url = url + "/"
    self.host, url = url.split("/", 1)
    if ":" in self.host:
      url, port = url.split(":", 1)
      self.port = int(port)
    self.path = "/" + url
    if self.scheme == "file":
      self.path = url
      self.host = "127.0.0.1"
    if self.scheme == "data":
      datatype, self.path = url.split(",", 1)
      self.host = self.host + "/" + datatype
    print("HOST:", self.host)  
    print("PATH:", self.path)  
    print("URL:", url)  

  def request(self, redCount = 0):
    if self.scheme == "file":
      with open(self.path) as file:
        content = file.read()
      return content
    if self.scheme == "data":
      return self.path
    s = socket.socket(
      family = socket.AF_INET,
      type = socket.SOCK_STREAM,
      proto  = socket.IPPROTO_TCP,
    )

    if self.scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname = self.host)

    s.connect((self.host, self.port))

    request = "GET {} HTTP/1.0\r\n".format(self.path)
    request += "Host: {}\r\n".format(self.host)
    request += "Connection: keep-alive\r\n".format(self.host)
    request += "Cache-Control: max-age=600\r\n".format(self.host)
    # request += "Accept-encoding: gzip\r\n".format(self.host)
    request += "User-Agent: rodrigao2000\r\n".format(self.host)
    request += "\r\n"
    s.send(request.encode("utf8"))

    self.response = s.makefile("r", encoding="utf-8", newline="\r\n")

    statusline = self.response.readline()
    version, status, explanation = statusline.split(" ", 2)
    print(statusline)

    response_headers = {}
    while True:
      line = self.response.readline()
      if line == "\r\n": break
      header, value = line.split(":", 1)
      response_headers[header.casefold()] = value.strip()

    bodySize = int(response_headers["content-length"])
    print(status)
    print(response_headers)
    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers
    
    if int(status) >= 300 and int(status) < 400:
      redCount += 1
      redirectURL = response_headers["location"]
      if "://" not in redirectURL:
        redirectURL = self.scheme + "://" + self.host + redirectURL
      if redCount> 2:
        return "too many redirects"
      newURL = URL(redirectURL)
      content  = newURL.request(redCount)
      s.close()
      return content

    if int(status) >= 200 and int(status) < 300:
      content = self.response.read(bodySize)
      s.close()
      return content
    
    return "error {}".format(status)
  
def show(body, vs):
    if vs:
      for c in body:
        print(c, end="") 
      return
    in_tag = False
    for c in body:
      if c == "<":
        in_tag = True
      elif c == ">":
        in_tag = False
      elif not in_tag:
        print(c, end="")
    
def load(url):
    body = url.request()
    show(body, url.viewSource)

if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))

