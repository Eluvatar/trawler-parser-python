trawler-parser-python
=====================

python parser library for using the Trawler service to throttle one's automated access to NationStates.net and parse NationStates.net API responses

## Usage ##

1. You must set `api.user_agent`, in accordance with [the API terms of Use](https://www.nationstates.net/pages/api.html#terms).
2. You must have a [trawler daemon](https://github.com/Eluvatar/trawler-daemon-c) running (this necessitates installing its dependencies).
3. You must also have `protoc-python` to compile the protocol buffer definitions used to talk to the daemon in the client submodule.  i.e. `aptitude install protobuf-compiler python-protobuf` or `dnf install protobuf-compiler protobuf-python`
4. You must also have `python-zmq` to talk to the trawler daemon. e.g. `pip install pyzmq` (If installing through pip and not your distribution, you may need to also install `python-dev` or `python-devel`).
5. You must check out the submodules.

Going through the steps:

### Compile and set up the daemon ###

*See the daemon's [README](https://github.com/Eluvatar/trawler-daemon-c/blob/master/README.md).*

### Check out the code: ###

```bash
$ git clone https://github.com/Eluvatar/trawler-parser-python.git parser
$ cd parser
$ git submodule init; git submodule update --init --recursive
```

### Compile the protocol buffer definitions: ###

```bash
$ cd client
$ protoc --proto_path=./protocol/ --python_out=. ./protocol/trawler.proto; cd ..
```

### Add the parser to your script: ###

```python
from parser import api
api.user_agent = PUT SOMETHING HERE
```

### Invoke the parser in your code: ###

```python
def get_region_wa_nations(region):
    region_nations = frozenset(api.request({'region':nation,'q':['nations']}).find("NATIONS").text.split(":"))
    wa_nations = frozenset(api.request({'wa':'1','q':['members']]).find("MEMBERS").text.split(","))
    return region_nations & wa_nations
```

### Complaints etc ###

This little library is by [Eluvatar](https://www.nationstates.net/nation=eluvatar). If it's broken, file an issue!
