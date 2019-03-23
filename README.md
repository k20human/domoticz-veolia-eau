# Get Veolia Eau teleinfo to Domoticz

## Install

```bash
sudo apt-get install python3 xvfb iceweasel
sudo pip install selenium
wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-arm7hf.tar.gz && tar xzf geckodriver-v0.23.0-arm7hf.tar.gz && sudo mv geckodriver /usr/local/bin && rm geckodriver-v0.23.0-arm7hf.tar.gz
git clone -b site/idf https://github.com/k20human/domoticz-veolia-eau.git
```

Copy ``config.json.exemple`` to ``config.json`` and fill with your Domoticz informations

Add to your cron tab (with ``crontab -e``):
```bash
30 7,12,17,22 * * * cd /home/pi/domoticz-veolia-eau && python3 execute.py
```

