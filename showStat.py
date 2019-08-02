import json
import getStat

dat = getStat.requestData()

print(json.dumps(dat))
