import requests
from config import webhook_url
import magic
import os
from config import rule_directory, mwdb_username, mwdb_password, mwdb_url, compiled_rules_directory
from mwdblib import MWDB
import hashlib

def create_rule_md5(rule_path): # Redundant code, dumb fix to circular import issue
    return hashlib.md5(open(rule_path,'rb').read()).hexdigest()

def post_to_webhook(data):
    # Send the triggered YARA rule to the Discord webhook
    req_body = {
        "username" : "YARHUNT-WEBHOOK"
    }
    req_body["embeds"] = [
        {
            "description" : "{0}".format(data),
            "title" : "Author {0} --> {1}".format(data["meta"]["author"], data["rule"])
        }
    ]
    uploaded = requests.post(webhook_url, json=req_body)

def download_yara_rule(url):
    # Download the attachment and do some simple verifications on the file type
    file_name = url.split("/")[6]
    uploaded = False
    if file_name.endswith(".yara"):
        with requests.get(url) as req:
            with open("/tmp/" + file_name, "wb") as f:
                f.write(req.content)
        if magic.from_file("/tmp/" + file_name) == "ASCII text":
            with open(rule_directory + file_name, "wb") as f:
                f.write(open("/tmp/" + file_name, "rb").read())
            uploaded = True   
        else:
            uploaded = False
        os.remove("/tmp/" + file_name)
    else:
        uploaded = False
    return uploaded

def delete_yara_rule(url):
    file_name = url.split("/")[6]
    with requests.get(url) as req:
        with open("/tmp/" + file_name, "wb") as f:
            f.write(req.content)
    target_file_hash = create_rule_md5("/tmp/" + file_name)
    for r, d, f in os.walk(compiled_rules_directory):
        for fi in f:
            print(fi)
            if fi == target_file_hash:
                os.remove(os.path.join(r,fi))

def upload_to_mwdb(file_name, file_path):
    mwdb = MWDB(api_url=mwdb_url)
    mwdb.login(username=mwdb_username, password=mwdb_password)
    print("Uploading file with hash {0}".format(file_name))
    mwdb.upload_file(file_name, open(file_path, "rb").read(), public=True)