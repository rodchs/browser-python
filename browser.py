import socket
import ssl

class URL: 
  def __init__(self, url):
    if "://" in url:
      self.scheme, url = url.split("://", 1)
    else:
      self.scheme, url = url.split(":", 1)
    assert self.scheme in ["http", "https", "file", "data"]
    
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
  def request(self):
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
    request += "Connection: close\r\n".format(self.host)
    request += "User-Agent: rodrigao2000\r\n".format(self.host)
    request += "\r\n"
    s.send(request.encode("utf8"))

    response = s.makefile("r", encoding="utf8", newline="\r\n")

    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)

    response_headers = {}
    while True:
      line = response.readline()
      if line == "\r\n": break
      header, value = line.split(":", 1)
      response_headers[header.casefold()] = value.strip()
      
    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers
    

    content = response.read()
    s.close()

    return content
  
def show(body):
    in_tag = False
    # in_entity = False
    # entity = []
    for c in body:
      if c == "<":
        in_tag = True
      elif c == ">":
        in_tag = False
      elif not in_tag:
        print(c, end="")
    
def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))

