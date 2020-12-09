#!/usr/bin/env python
# coding=utf-8
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import logging
from tqdm import tqdm
logger = logging.getLogger(__name__)


class Json:
    def __init__(self, file_path: str, lines: int = -1):
        self.file_path = file_path
        self.lines = lines

    @staticmethod
    def loads(dump):
        return json.loads(dump, encoding="utf-8")

    @staticmethod
    def dumps(obj):
        return json.dumps(obj, encoding="utf-8", ensure_ascii=False)

    def load(self):
        with open(self.file_path, 'r', encoding='utf-8') as fr:
            return json.load(fr)

    def loadl(self):
        with open(self.file_path, 'r', encoding='utf-8') as fr:
            for ix, line in tqdm(enumerate(fr)):
                if ix < 5:
                    logger.info("line %s: %s", ix, line)
                if self.lines < 0 or self.lines < ix:
                    yield json.loads(line.strip())
                else:
                    break

    def dump(self, obj):
        with open(self.file_path, 'w', encoding='utf-8') as fw:
            json.dump(obj, fw, ensure_ascii=False, indent=2)

    def dumpl(self, obj):
        with open(self.file_path, 'w', encoding='utf-8') as fw:
            for line in obj:
                fw.write(json.dumps(line, ensure_ascii=False)+'\n')

    @staticmethod
    def pretty(obj):
        return json.dumps(obj, ensure_ascii=False, indent=4)
