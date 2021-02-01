# TODO: Excluded "cid" in "_source"

def genData(_index, _id, _doc: {}):
    yield {
        "_index": _index,
        "_id": _id,
        "_source": {
            "cid": _id,
            "data": [{str(k).lower(): v for k, v in _doc.items()}]
        }
    }


def genDataUpd(_index, _id, _doc: {}):
    yield {
        "_index": _index,
        "_id": _id,
        '_op_type': 'update',
        "script": {
            "lang": "painless",
            "params": {
                "tag": {str(k).lower(): v for k, v in _doc.items()},
                "timestamp": _doc["timestamp"]
            },
            "source": """
                /* This part is the logic to check whether or not there were an existing timestamp
                If there was, overwrite the old one. If not, add it to the `data` list */

                boolean x = false;
                try {
                    for (int i = 0; i < ctx._source.data.length; ++i) {
                        if (ctx._source.data[i]["timestamp"] == params.timestamp) {
                            ctx._source.data[i] = params.tag;
                            x = true;
                        }
                    }
                }
                catch (Exception e) {
                    /* Doing nothing */
                }
                
                if (x == false) {
                    ctx._source.data.add(params.tag)
                }
            """
        }
    }

# TODO: Add update method without timestamp
def genDataUpdNoTimestamp(_index, _id, _doc: {}):
    yield {
        "_index": _index,
        "_id": _id,
        '_op_type': 'update',
        "script": {
            "lang": "painless",
            "params": {
                "tag": {str(k).lower(): v for k, v in _doc.items()},
                "stockcode": _doc["StockCode"]
            },
            "source": """
                /* This part is the logic to check whether or not there were an existing stockcode
                If there was, overwrite the old one. If not, add it to the `data` list */

                boolean x = false;
                try {
                    for (int i = 0; i < ctx._source.data.length; ++i) {
                        if (ctx._source.data[i]["stockcode"] == params.stockcode) {
                            ctx._source.data[i] = params.tag;
                            x = true;
                        }
                    }
                }
                catch (Exception e) {
                    /* Doing nothing */
                }
                
                if (x == false) {
                    ctx._source.data.add(params.tag)
                }
            """
        }
    }