#!/usr/bin/env python
import gspread, json, requests, pprint, argparse
from oauth2client.service_account import ServiceAccountCredentials

class TaigaStats:
    def __init__(self, taiga_creds):
        with open(taiga_creds) as data_file:
            auth_data = json.loads(data_file.read())
        self.host = auth_data["host"]
        self.auth_token = self.auth(auth_data)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

    def auth(self, auth_data):
        data_json = {
            "username": auth_data["username"],
            "password": auth_data["password"],
            "type": "normal"
        }
        return requests.post(
            self.host+"/api/v1/auth",
            headers={"Content-Type": "application/json"},
            json=data_json
        ).json()["auth_token"]

    def get_data(self, url):
        return requests.get(
            self.host+url,
            headers=self.headers
        ).json()

    def get_milestones(self):
        return self.get_data("/api/v1/milestones")

    def get_projects(self):
        return self.get_data("/api/v1/projects")

    def get_stats(self):
        projects = []
        all_milestones = self.get_milestones()
        for project in self.get_projects():
            milestones = []
            for milestone in all_milestones:
                if milestone["project_extra_info"]["name"] == project["name"]:
                    users = {}
                    for user_story in milestone["user_stories"]:
                        if user_story["is_closed"] and user_story["assigned_to"] is not None:
                            username = user_story["assigned_to_extra_info"]["full_name_display"]
                            if username in users:
                                users[username] += user_story["total_points"]
                            else:
                                users[username] = user_story["total_points"]
                    milestones.append({
                        "name": milestone["name"],
                        "users": users,
                        "total_points": milestone["total_points"]
                    })
            projects.append({
                "name": project["name"],
                "sprints": milestones
            })
        return projects

class GSheets:
    SPREADSHEETS_URL = 'https://spreadsheets.google.com/feeds';
    
    def __init__(self, document_name, gsheets_creds):
        # use creds to create a client to interact with the Google Drive API
        scope = [this.SPREADSHEETS_URL]
        creds = ServiceAccountCredentials.from_json_keyfile_name(gsheets_creds, scope)
        self.document = document_name
        self.client = gspread.authorize(creds)

    def select_sheet(self, name):
        try:
            self.sheet = self.client.open(self.document).worksheet(name)
            return True
        except gspread.exceptions.WorksheetNotFound as e:
            print("WorksheetNotFound: ", e)
            return False

    def find_coords(self, names):
        try:
            coords = (self.sheet.find(names[0]).row, self.sheet.find(names[1]).col)
        except gspread.exceptions.CellNotFound as e:
            print("CellNotFound: ", e)
            coords = None
        return coords

    def update(self, coord_name1, coord_name2, val):
        coords = self.find_coords((coord_name1, coord_name2))
        if coords is not None:
            self.sheet.update_cell(coords[0], coords[1], str(val).replace('.', ','))

def sync_projects(taiga, gs, output_table):
    stats = taiga.get_stats()
    for project in stats:
        if not gs.select_sheet(project["name"]):
            continue
        for sprint in project["sprints"]:
            for username, points in sprint["users"].items():
                # round 3.0 etc points
                if int(points) == points:
                    points = int(points)
                gs.update(sprint["name"], username, points)
            gs.update(sprint["name"], output_table, sprint["total_points"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tool is used for loading Taiga.io stats to GSheets"
    )
    parser.add_argument(
        "--sheet-name",
        help="The name of sheet in Google Sheets",
        required=True
    )
    parser.add_argument(
        "--output-table",
        help="The name of output table",
        required=True
    )
    parser.add_argument(
        "--taiga-creds",
        help="Taiga.io credentials (path to json file) with 'host', 'username' and 'password' keys",
        default="taiga_login.json",
        required=False
    )
    parser.add_argument(
        "--gsheets-creds",
        help="Google Sheets credentials (path to json file)",
        default="gsheets_login.json",
        required=False
    )
    args = parser.parse_args()
    
    taiga = TaigaStats(args["--taiga-creds"])
    gsheets = GSheets(args["--sheet-name"], args["--gsheets-creds"])
    sync_projects(taiga, gsheets)
