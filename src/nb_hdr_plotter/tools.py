"""
   Copyright 2022 Stefano Lottini

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

tools.py
"""


def groupBy(iterable, keyer, valuer=lambda e: e):
    dictionary = {}
    done = 0
    for item in iterable:
        key = keyer(item)
        if key not in dictionary:
            dictionary[key] = [valuer(item)]
        else:
            dictionary[key].append(valuer(item))
        done += 1
    return dictionary
