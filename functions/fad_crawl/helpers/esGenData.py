def genData(_index, _id, _doc: {}):
    yield {
        "_index": _index,
        "_id": _id,
        "_source": {
            "cid": _id,
            "data": [{k: v for k, v in _doc.items()}]
        }
    }


def genDataUpd(_index, _id, _doc: {}):
    yield {
        "_index": _index,
        "_id": _id,
        '_op_type': 'update',
        "script": {
                    "inline": "ctx._source.data.add(params.tag)",
                    "lang": "painless",
                    "params": {
                        "tag": {k: v for k, v in _doc.items()}
                    }

        }
    }