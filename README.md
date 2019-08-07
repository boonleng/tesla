Tesla Data Logger
===

Fetch information from a Tesla vehicle

![Figure](blob/screenshot.png)

## Recommended Setup Procedures

I am using this on a macOS computer and I usually put all open-source software under ~/Developer/. So, the following instructions are how I set it up on my computer. Feel free to deviate. Obviously, do all of these in a Terminal. First thing is to change directorty to ~/Developer, clone the project. Then, you will get the folder ~/Developer/tesla
```shell
git clone https://github.com/boonleng/tesla.git
```

Run the script once
```shell
getStat.py -v -w
```
or
```shell
python getStat.py -v -w
```
which will prompt you for your Tesla account username and password. Don't worry, they are not stored in plain text. The Keychain Access is responsible for keeping the information safe. The software has not been tested extensively so it is very likely to contains bugs. Please let me know and I'll try my best to fix them.

## Cronjob

Use the cronjob utility to schedule a periodical retrieval. My cron table looks like:

```
*/15 * * * *    ${HOME}/Developer/tesla/getStat.py -w
```

NOTE: Update the home path to reflect where you store the scripts.

After a few days, you would end up with a bunch of log files under ${HOME}/Documents/Tesla/

```
.
├── 20190724
│   ├── 20190724-1245.json
│   ├── 20190724-1300.json
│   ├── 20190724-1315.json
│   ├── 20190724-1330.json
.
.
├── 20190725
│   ├── 20190725-0830.json
│   ├── 20190725-0845.json
│   ├── 20190725-0900.json
.
.
```

Congratulations, you are now logging the information from your Tesla vehicle.
