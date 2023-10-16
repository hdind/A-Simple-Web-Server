import http.server
import os
import logging


class RequestHandler(http.server.BaseHTTPRequestHandler):    
    Page = '''
        <html>
            <body>
                <table>
                    <tr>  <td>Header</td>         <td>Value</td>          </tr>
                    <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
                    <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
                    <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
                    <tr>  <td>Command</td>        <td>{command}</td>      </tr>
                    <tr>  <td>Path</td>           <td>{path}</td>         </tr>
                </table>
            </body>
        </html>
    '''
    
    def do_GET(self):
        try:
            full_path = os.getcwd() + self.path
            logging.info(full_path)

            if not os.path.exists(full_path):
                raise Exception(f'{self.path} not found')
            elif os.path.isfile(full_path):
                logging.info('handling file')
                self.handle_file(full_path)
            else:
                raise Exception(f'Unknown object {self.path}')
        except Exception as e:
            logging.info('handling error')
            self.handle_error(e)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            logging.info('sending content')
            self.send_content(content)
        except IOError as e:
            logging.info('something went wrong')
            msg = f'{self.path} cannot be read: {e}'
            self.handle_error(msg)

    Error_Page = """
        <html>
            <body>
                <h1>Error accessing {path}</h1>
                <p>{msg}</p>
            </body>
        </html>
        """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'), 404)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def create_page(self):  
        values = {
            'date_time'   : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command'     : self.command,
            'path'        : self.path
        }
        page = self.Page.format(**values)
        return page

    def send_page(self, page):    
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page.encode('utf-8'))
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    serverAddress = ('', 8080)
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()