import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

import stravalib


def main():
  client_id = input("Enter your Strava API Client ID:\n")
  client_secret = input("Enter your Strava API Client Secret:\n")
  hostName = "localhost"
  serverPort = 9321
  strava_client = stravalib.Client()

  class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
      qs = parse_qs(self.path)
      code = qs.get("code")
      if code:
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        access_info = strava_client.exchange_code_for_token(
          client_id=client_id,
          client_secret=client_secret,
          code=code,
        )
        print(f"Access token: {access_info['access_token']}")
        print(f"Refresh token: {access_info['refresh_token']}")
        self.wfile.write(bytes(json.dumps(access_info), encoding="utf-8"))
      else:
        self.send_error(400, explain="No code in URL, please try again")
        print("No code in URL, please try again")
      threading.Thread(target=self.server.shutdown, daemon=True).start()

  serverAddress = f"http://{hostName}:{serverPort}"
  server = HTTPServer((hostName, serverPort), MyServer)
  print(f"Server started {serverAddress}")
  webbrowser.open_new_tab(
    strava_client.authorization_url(
      client_id=client_id,
      redirect_uri=serverAddress,
      scope=["activity:write", "activity:read_all"],
    )
  )
  server.serve_forever()


if __name__ == "__main__":
  main()
