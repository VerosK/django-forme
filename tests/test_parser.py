# coding: utf-8
from __future__ import unicode_literals

import pytest
from django import template

from forme.parser import FormeParser


def parse_template(content):
    lexer = template.Lexer(content, '')
    parser = template.Parser(lexer.tokenize())
    token = parser.next_token()
    return parser, token


class TestFormeParse:
    def test_valid_actions(self, forme):
        assert 'hide' not in forme.valid_actions

        forme.tag_name = 'field'
        assert 'hide' in forme.valid_actions

    def test_action_no_target(self, node_mock):
        parser, token = parse_template('{% forme using %}{% endforme %}')
        FormeParser(parser, token).parse()
        tag, targets, action, nodelist = node_mock.call_args[0]
        assert tag == 'forme'
        assert targets == []
        assert action == 'using'
        assert nodelist == []

    def test_parse_target(self, forme):
        vars = lambda variables: [variable.var for variable in variables]
        assert vars(forme.parse_target(['form'])) == ['form']
        assert vars(forme.parse_target(['form1', 'form2'])) \
               == ['form1', 'form2']
        assert vars(forme.parse_target(['"form1 form2"'])) \
               == ['"form1"', '"form2"']
        assert vars(forme.parse_target(['"form1 form2"', 'form3'])) \
                == ['"form1"', '"form2"', 'form3']

    def test_parse_action(self, forme):
        assert forme.parse_action(['using']) == ('using', True)
        assert forme.parse_action(['replace']) == ('replace', True)
        assert forme.parse_action(['default']) == ('default', False)

    def test_parse_paired_empty(self, node_mock):
        parser, token = parse_template('{% forme form using %}{% endforme %}')
        FormeParser(parser, token).parse()
        tag, targets, action, nodelist = node_mock.call_args[0]
        assert tag == 'forme'
        assert action == 'using'
        assert nodelist == []

    def test_parse_paired(self, node_mock):
        tpl = '{% forme form using %}{{ test }}{% endforme %}'
        parser, token = parse_template(tpl)
        FormeParser(parser, token).parse()
        tag, targets, action, nodelist = node_mock.call_args[0]
        assert tag == 'forme'
        assert action == 'using'
        assert nodelist != []
