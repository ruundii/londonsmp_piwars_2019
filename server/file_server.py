import os
import html
import datetime
import tornado.web


class StaticFileRequestHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
    def set_extra_headers(self, path):
        if "js\\" in path.lower() or "svgs\\" in path.lower():
            self.set_header("Cache-control", "no-cache")

class FileRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self):
        try:
            if 'files' in self.request.path:
                path = os.path.join(os.getcwd(), 'files')
            elif 'svgs' in self.request.path:
                path = os.path.join(os.getcwd(), 'svgs')
            list = os.listdir(path)
        except os.error:
            raise tornado.web.HTTPError(status_code=403, log_message="No permission to list directory.")
        list.sort(key=lambda a: a.lower())
        responseBody = "{\"files\":[\n";
        for name in list:
            fullname = os.path.join(path, name)
            # Append / for directories or @ for symbolic links
            if not os.path.isdir(fullname) and not os.path.islink(fullname):
                responseBody=responseBody+'{{\"name\":\"{}\", \"lastModifiedDate\":\"{:%Y-%m-%d %H:%M:%S}\"}},\n'.format(html.escape(name), self.modification_date(fullname))
        responseBody = responseBody.rstrip('\n').rstrip(',')+"\n]}\n"
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish(responseBody)

    def post(self):
        fileName   = self.get_body_argument('fileName')
        fileContent = self.get_body_argument('fileContent')
        name, ext = os.path.splitext(fileName)

        pathBackup = os.path.join(os.getcwd(), 'backup_files')

        if 'files' in self.request.path:
            path = os.path.join(os.getcwd(), 'files')
            if ext not in ('.xml'):
                raise tornado.web.HTTPError(status_code=403, log_message="File extension not allowed.")
            fullname = os.path.join(path, fileName)
            fullnameBackup = os.path.join(pathBackup, name + '-{date:%Y-%m-%d-%H-%M-%S}.xml'.format(
                date=datetime.datetime.now()))
        elif 'svgs' in self.request.path:
            path = os.path.join(os.getcwd(), 'svgs')
            if ext not in ('.svg'):
                raise tornado.web.HTTPError(status_code=403, log_message="File extension not allowed.")
            fullname = os.path.join(path, fileName)
            fullnameBackup = os.path.join(pathBackup, name +'-{date:%Y-%m-%d-%H-%M-%S}.svg'.format(date=datetime.datetime.now()))

        with open(fullname, "w") as target_file:
            print(fileContent, file=target_file)
        with open(fullnameBackup, "w") as target_file:
            print(fileContent, file=target_file)

        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish('{"status":"success"}')

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)
