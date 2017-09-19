# Get Veolia Eau teleinfo to Domoticz

## Install

```bash
sudo apt-get install python3 python3-xlrd
git clone https://github.com/k20human/domoticz-veolia-eau.git
```

Copy ``config.json.exemple`` to ``config.json`` and fill with your Domoticz informations

Add to your cron tab (with ``crontab -e``):
```bash
30 7,12,17,22 * * * cd /home/pi/domoticz-veolia-eau && python3 execute.py
```

