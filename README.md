# YarHunt

## About
YarHunt is a project created during an 8hr hackathon.\
It is designed to be used as a collection / hunting system for malware samples.

YarHunt will download samples from Malware Bazaar and Malshare, then run Yara rules on the samples, and save all matches.\
Discord is used as an easy front end, which allows a small set of commands to be used:
- Upload new Yara rule
- Remove Yara rule
- See active rules
- See active "jobs" (threads downloading new samples)

The malware samples of interest are saved locally, and sent to an MWDB instance.\
YarHunt per default uploads samples to the MWDB instance run by CERT PL (https://mwdb.cert.pl).



## Config
A config file placed next to the "bot.py" file is needed.\
This config file should contain the following constants:
```
# Path constants
rule_directory = "<Path to yara rules directory>"
compiled_rules_directory = "<Path to directory to store compiled yara rules in>"
malware_cage = "<Directory malware should be saved in>"
rule_match_folder = "<Directory samples should be stored in>"
bazaar_zip_name = "hourlybzr"
bazaar_unzip_name = "unzipped_hourlybzr"
malshare_folder = "malshare/"

# Discord stuff
bot_token = "<Discord bot token>"
webhook_url = "<Webhook URL>"

# APIs 
bazaar_hourly_endpoint = "https://datalake.abuse.ch/malware-bazaar/hourly/"
malshare_key_two = "<Malshare API key #1>"
malshare_key_one = "<Malshare API key #2>"
malshare_api_endpoint = "https://malshare.com/api.php"


# MWDB 
mwdb_username = "<MWDB username>"
mwdb_password = "<MWDB password>"
mwdb_url = "https://mwdb.cert.pl/api/" # Or your own MWDB URL 
```
## Usage
Prefix for the bot is "!".\
List of commands are available with "!help".

```
CmdHandlerCog:
  delete 
  jobs   
  rules  
  upload 
​No Category:
  help   Shows this message
```
The help menu is the builtin menu provided by the Discord.Py library

To upload a rule, add it as an attachment to the message, with the "!upload" command.\
Same goes for deleting rules.
