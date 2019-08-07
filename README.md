Tesla Data Logger
===

Fetch information from a Tesla vehicle

![Figure](blob/screenshot.png)

## Recommended Installation

I am using macOS and I usually put all open-source software under ~/Developer/. So, while in ~/Developer, clone the project so you would have a folder ~/Developer/tesla
```shell
git clone https://github.com/boonleng/tesla.git
```

Run the script once
```shell
getStat.py
```
or
```shell
python getStat.py
```

## Cronjob

Use the cronjob utility to schedule a periodical retrieval. My cron table looks like:

```
*/15 * * * *    ${HOME}/Developer/tesla/getStat.py -w
```

NOTE: Replace the home path of your utility.

You would end up with a bunch of log files under ${HOME}/Documents/Tesla/

```
.
├── 20190724
│   ├── 20190724-1244.json
│   ├── 20190724-1245.json
│   ├── 20190724-1250.json
│   ├── 20190724-1255.json
.
.
├── 20190725
│   ├── 20190725-0830.json
│   ├── 20190725-0843.json
│   ├── 20190725-0845.json
.
.
```
