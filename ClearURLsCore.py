'''
* ClearURLs
* Copyright (c) 2019 Kevin Röbert
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Lesser General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Lesser General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from urllib.parse import unquote
from urllib.request import urlopen
import json
import re

'''
 * Python class that used the ClearURLs data.min.json
 * to clean urls. Also redirections included.
 *
 * @param dataURL The url to the data.min.json,
 * default is the gitlab repo of ClearURLs
'''
class ClearURLsCore:
    def __init__(self, dataURl
        = "https://gitlab.com/KevinRoebert/ClearUrls/raw/master/data/data.min.json"):
        self.dataURL = dataURl
        self.pages = {}
        self.initRules()

    def initRules(self):
        # download ClearURLs rule set
        #data = urlopen(self.dataURL).read()

        #load rule set from local file
        data = open("data.min.json").read()
        json_data = json.loads(data)

        # extract and expand rules
        for provider in json_data["providers"]:
            urlPattern = json_data["providers"][provider]["urlPattern"]
            self.pages[urlPattern] = {
                "rules": [],
                "exceptions": [],
                "redirections": []
            }

            for rule in json_data["providers"][provider]["rules"]:
                self.pages[urlPattern]["rules"].append("([\\/|\\?]|(&|&amp;))("+rule+"=[^\\/|\\?|&]*)")

            self.pages[urlPattern]["exceptions"] = json_data["providers"][provider]["exceptions"]
            self.pages[urlPattern]["redirections"] = json_data["providers"][provider]["redirections"]

    def clean(self, url):
        domain = re.sub("\\?.*", "", url)
        fields = "?"+re.sub(".*?\\?", "", url)

        for page in self.pages:
            if re.search(page, url):
                for exception in self.pages[page]["exceptions"]:
                    if re.search(exception, url):
                        return url
                for redirection in self.pages[page]["redirections"]:
                    if re.search(redirection, url):
                        result = re.search(redirection, url).group(1)
                        return unquote(result)
                for rule in self.pages[page]["rules"]:
                    fields = re.sub(rule, "", fields)
        finalFields = re.findall("[^\\/|\\?|&]+=[^\\/|\\?|&]+", fields)
        if len(finalFields) > 0:
            return domain + "?" + "&".join(finalFields);
        return domain
