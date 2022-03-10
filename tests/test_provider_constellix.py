#
#
#

from os.path import dirname, join
from requests import HTTPError
from requests_mock import ANY, mock as requests_mock
from unittest import TestCase
from unittest.mock import Mock, PropertyMock, call

from octodns.record import Record
from octodns.provider.yaml import YamlProvider
from octodns.zone import Zone

from octodns_constellix import ConstellixProvider, ConstellixClientBadRequest


class TestConstellixProvider(TestCase):
    expected = Zone('unit.tests.', [])
    source = YamlProvider('test', join(dirname(__file__), 'config'))
    source.populate(expected)

    # Our test suite differs a bit, add our NS and remove the simple one
    expected.add_record(Record.new(expected, 'under', {
        'ttl': 3600,
        'type': 'NS',
        'values': [
            'ns1.unit.tests.',
            'ns2.unit.tests.',
        ]
    }))

    # Add some ALIAS records
    expected.add_record(Record.new(expected, '', {
        'ttl': 1800,
        'type': 'ALIAS',
        'value': 'aname.unit.tests.'
    }))

    # Add a dynamic record
    expected.add_record(Record.new(expected, 'www.dynamic', {
        'ttl': 300,
        'type': 'A',
        'values': [
            '1.2.3.4',
            '1.2.3.5'
        ],
        'dynamic': {
            'pools': {
                'two': {
                    'values': [{
                        'value': '1.2.3.4',
                        'weight': 1
                    }, {
                        'value': '1.2.3.5',
                        'weight': 1
                    }],
                },
            },
            'rules': [{
                'pool': 'two',
            }],
        },
    }))

    for record in list(expected.records):
        if record.name == 'sub' and record._type == 'NS':
            expected._remove_record(record)
        if record.name == '' and record._type == 'NS':
            expected._remove_record(record)

    expected_healthcheck = Zone('unit.tests.', [])
    source = YamlProvider('test', join(dirname(__file__), 'config'))
    source.populate(expected_healthcheck)

    # Our test suite differs a bit, add our NS and remove the simple one
    expected_healthcheck.add_record(Record.new(expected_healthcheck, 'under', {
        'ttl': 3600,
        'type': 'NS',
        'values': [
            'ns1.unit.tests.',
            'ns2.unit.tests.',
        ]
    }))

    # Add some ALIAS records
    expected_healthcheck.add_record(Record.new(expected_healthcheck, '', {
        'ttl': 1800,
        'type': 'ALIAS',
        'value': 'aname.unit.tests.'
    }))

    # Add a dynamic record
    expected_healthcheck.add_record(
        Record.new(expected_healthcheck, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4',
                '1.2.3.5'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }, {
                            'value': '1.2.3.5',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
            'octodns': {
                'constellix': {
                    'healthcheck': {
                        'sonar_port': 80,
                        'sonar_regions': [
                            'ASIAPAC',
                            'EUROPE'
                        ],
                        'sonar_type': 'TCP'
                    }
                }
            }
        })
    )

    for record in list(expected_healthcheck.records):
        if record.name == 'sub' and record._type == 'NS':
            expected_healthcheck._remove_record(record)
            break

    expected_healthcheck_world = Zone('unit.tests.', [])
    source = YamlProvider('test', join(dirname(__file__), 'config'))
    source.populate(expected_healthcheck_world)

    # Our test suite differs a bit, add our NS and remove the simple one
    expected_healthcheck_world.add_record(
        Record.new(expected_healthcheck_world, 'under', {
            'ttl': 3600,
            'type': 'NS',
            'values': [
                'ns1.unit.tests.',
                'ns2.unit.tests.',
            ]
        })
    )

    # Add some ALIAS records
    expected_healthcheck_world.add_record(
        Record.new(expected_healthcheck_world, '', {
            'ttl': 1800,
            'type': 'ALIAS',
            'value': 'aname.unit.tests.'
        })
    )

    # Add a dynamic record
    expected_healthcheck_world.add_record(
        Record.new(expected_healthcheck_world, 'www.dynamic', {
            'ttl': 300,
            'type': 'AAAA',
            'values': [
                '2601:644:500:e210:62f8:1dff:feb8:947a',
                '2601:642:500:e210:62f8:1dff:feb8:947a'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '2601:644:500:e210:62f8:1dff:feb8:947a',
                            'weight': 1
                        }, {
                            'value': '2601:642:500:e210:62f8:1dff:feb8:947a',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
            'octodns': {
                'constellix': {
                    'healthcheck': {
                        'sonar_port': 80,
                        'sonar_regions': [
                            'WORLD'
                        ],
                        'sonar_type': 'HTTP'
                    }
                }
            }
        })
    )

    for record in list(expected_healthcheck_world.records):
        if record.name == 'sub' and record._type == 'NS':
            expected_healthcheck_world._remove_record(record)
            break

    expected_dynamic = Zone('unit.tests.', [])
    source = YamlProvider('test', join(dirname(__file__), 'config'))
    source.populate(expected_dynamic)

    # Our test suite differs a bit, add our NS and remove the simple one
    expected_dynamic.add_record(Record.new(expected_dynamic, 'under', {
        'ttl': 3600,
        'type': 'NS',
        'values': [
            'ns1.unit.tests.',
            'ns2.unit.tests.',
        ]
    }))

    # Add some ALIAS records
    expected_dynamic.add_record(Record.new(expected_dynamic, '', {
        'ttl': 1800,
        'type': 'ALIAS',
        'value': 'aname.unit.tests.'
    }))

    # Add a dynamic record
    expected_dynamic.add_record(Record.new(expected_dynamic, 'www.dynamic', {
        'ttl': 300,
        'type': 'A',
        'values': [
            '1.2.3.4',
            '1.2.3.5'
        ],
        'dynamic': {
            'pools': {
                'one': {
                    'fallback': 'two',
                    'values': [{
                        'value': '1.2.3.6',
                        'weight': 1
                    }, {
                        'value': '1.2.3.7',
                        'weight': 1
                    }],
                },
                'two': {
                    'values': [{
                        'value': '1.2.3.4',
                        'weight': 1
                    }, {
                        'value': '1.2.3.5',
                        'weight': 1
                    }],
                },
            },
            'rules': [{
                'geos': [
                    'AS',
                    'EU-ES',
                    'EU-UA',
                    'EU-SE',
                    'NA-CA-NL',
                    'OC'
                ],
                'pool': 'one'
            }, {
                'pool': 'two',
            }],
        }
    }))

    for record in list(expected_dynamic.records):
        if record.name == 'sub' and record._type == 'NS':
            expected_dynamic._remove_record(record)
        if record.name == '' and record._type == 'NS':
            expected_dynamic._remove_record(record)

    def test_populate(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        # Bad auth
        with requests_mock() as mock:
            mock.get(ANY, status_code=401,
                     text='{"errors": ["Unable to authenticate token"]}')

            with self.assertRaises(Exception) as ctx:
                zone = Zone('unit.tests.', [])
                provider.populate(zone)
            self.assertEqual('Unauthorized', str(ctx.exception))

        with requests_mock() as mock:
            mock.get(ANY, status_code=401,
                     text='{"errors": ["Unable to authenticate token"]}')

            with self.assertRaises(Exception) as ctx:
                provider._sonar.agents
            self.assertEqual('Unauthorized', str(ctx.exception))

        # Bad request
        with requests_mock() as mock:
            mock.get(ANY, status_code=400,
                     text='{"errors": ["\\"unittests\\" is not '
                          'a valid domain name"]}')

            with self.assertRaises(Exception) as ctx:
                zone = Zone('unit.tests.', [])
                provider.populate(zone)
            self.assertEqual('\n  - "unittests" is not a valid domain name',
                             str(ctx.exception))

        with requests_mock() as mock:
            mock.get(ANY, status_code=400,
                     text='error text')

            with self.assertRaises(Exception) as ctx:
                provider._sonar.agents
            self.assertEqual('\n  - error text',
                             str(ctx.exception))

        # General error
        with requests_mock() as mock:
            mock.get(ANY, status_code=502, text='Things caught fire')

            with self.assertRaises(HTTPError) as ctx:
                zone = Zone('unit.tests.', [])
                provider.populate(zone)
            self.assertEqual(502, ctx.exception.response.status_code)

        # Non-existent zone doesn't populate anything
        with requests_mock() as mock:
            mock.get(ANY, status_code=404,
                     text='<html><head></head><body></body></html>')

            zone = Zone('unit.tests.', [])
            provider.populate(zone)
            self.assertEqual(set(), zone.records)

        with requests_mock() as mock:
            mock.get(ANY, status_code=404, text='')
            with self.assertRaises(Exception) as ctx:
                provider._sonar.agents
            self.assertEqual('Not Found', str(ctx.exception))

        # Sonar Normal response
        provider = ConstellixProvider('test', 'api', 'secret')
        with requests_mock() as mock:
            mock.get(ANY, status_code=200, text='[]')
            agents = provider._sonar.agents
            self.assertEqual({}, agents)
            agents = provider._sonar.agents

        provider = ConstellixProvider('test', 'api', 'secret', 0.01)
        with requests_mock() as mock:
            mock.get(ANY, status_code=200, text='[]')
            agents = provider._sonar.agents

        provider = ConstellixProvider('test', 'api', 'secret', 1.01)
        with requests_mock() as mock:
            mock.get(ANY, status_code=200, text='[]')
            agents = provider._sonar.agents

        provider = ConstellixProvider('test', 'api', 'secret')
        # No diffs == no changes
        with requests_mock() as mock:
            base = 'https://api.dns.constellix.com/v1'
            with open('tests/fixtures/constellix-domains.json') as fh:
                mock.get(f'{base}/domains', text=fh.read())
            with open('tests/fixtures/constellix-records.json') as fh:
                mock.get(f'{base}/domains/123123/records', text=fh.read())
            with open('tests/fixtures/constellix-pools.json') as fh:
                mock.get(f'{base}/pools/A', text=fh.read())
            with open('tests/fixtures/constellix-geofilters.json') as fh:
                mock.get(f'{base}/geoFilters', text=fh.read())

                zone = Zone('unit.tests.', [])
                provider.populate(zone)
                self.assertEqual(17, len(zone.records))
                changes = self.expected_dynamic.changes(zone, provider)
                self.assertEqual(0, len(changes))

        # 2nd populate makes no network calls/all from cache
        again = Zone('unit.tests.', [])
        provider.populate(again)
        self.assertEqual(17, len(again.records))

        # bust the cache
        del provider._zone_records[zone.name]

    def test_apply(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        resp = Mock()
        resp.json = Mock()
        provider._client._request = Mock(return_value=resp)

        # non-existent domain, create everything
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808520,
                "name": "unit.tests.:www.dynamic:A:two",
            }]   # pool created in apply
        ]

        plan = provider.plan(self.expected)

        # No ignored, no excluded, no unsupported
        n = len(self.expected.records) - 7
        self.assertEqual(n, len(plan.changes))
        self.assertEqual(n, provider.apply(plan))

        provider._client._request.assert_has_calls([
            # get all domains to build the cache
            call('GET', '/domains'),
            # created the domain
            call('POST', '/domains', data={'names': ['unit.tests']})
        ])

        # Check we tried to get our pool
        provider._client._request.assert_has_calls([
            # get all pools to build the cache
            call('GET', '/pools/A'),
            # created the pool
            call('POST', '/pools/A', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "1.2.3.4",
                    "weight": 1
                }, {
                    "value": "1.2.3.5",
                    "weight": 1
                }]
            })
        ])

        # These two checks are broken up so that ordering doesn't break things.
        # Python3 doesn't make the calls in a consistent order so different
        # things follow the GET / on different runs
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/SRV', data={
                'roundRobin': [{
                    'priority': 10,
                    'weight': 20,
                    'value': 'foo-1.unit.tests.',
                    'port': 30
                }, {
                    'priority': 12,
                    'weight': 20,
                    'value': 'foo-2.unit.tests.',
                    'port': 30
                }],
                'name': '_srv._tcp',
                'ttl': 600,
            }),
        ])

        self.assertEqual(22, provider._client._request.call_count)

        provider._client._request.reset_mock()

        provider._client.records = Mock(return_value=[
            {
                'id': 11189897,
                'type': 'A',
                'name': 'www',
                'ttl': 300,
                'recordOption': 'roundRobin',
                'value': [
                    '1.2.3.4',
                    '2.2.3.4',
                ]
            }, {
                'id': 11189898,
                'type': 'A',
                'name': 'ttl',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [
                    '3.2.3.4'
                ]
            },  {
                'id': 11189899,
                'type': 'ALIAS',
                'name': 'alias',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [{
                    'value': 'aname.unit.tests.'
                }]
            }, {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": None,
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                },
                {
                    "value": "1.2.3.5",
                    "weight": 1
                }
            ]
        }])

        # Domain exists, we don't care about return
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:one"
            }]  # pool created in apply
        ]

        wanted = Zone('unit.tests.', [])
        wanted.add_record(Record.new(wanted, 'ttl', {
            'ttl': 300,
            'type': 'A',
            'value': '3.2.3.4'
        }))

        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
        }))

        plan = provider.plan(wanted)
        self.assertEqual(4, len(plan.changes))
        self.assertEqual(4, provider.apply(plan))

        # recreate for update, and deletes for the 2 parts of the other
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/A', data={
                'roundRobin': [{
                    'value': '3.2.3.4'
                }],
                'name': 'ttl',
                'ttl': 300
            }),
            call('PUT', '/pools/A/1808521', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "1.2.3.4",
                    "weight": 1
                }],
                'id': 1808521,
                'geofilter': 1
            }),
            call('DELETE', '/domains/123123/records/A/11189897'),
            call('DELETE', '/domains/123123/records/A/11189898'),
            call('DELETE', '/domains/123123/records/ANAME/11189899'),
        ], any_order=True)

    def test_apply_healthcheck(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        resp = Mock()
        resp.json = Mock()
        provider._client._request = Mock(return_value=resp)

        # non-existent domain, create everything
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808520,
                "name": "unit.tests.:www.dynamic:A:two",
            }]   # pool created in apply
        ]

        sonar_resp = Mock()
        sonar_resp.json = Mock()
        type(sonar_resp).headers = PropertyMock(return_value={
            "Location": "http://api.sonar.constellix.com/rest/api/tcp/52906"
        })
        sonar_resp.headers = Mock()
        provider._sonar._request = Mock(return_value=sonar_resp)

        sonar_resp.json.side_effect = [
            [{
                "id": 1,
                "name": "USWAS01",
                "label": "Site 1",
                "location": "Washington, DC, U.S.A",
                "country": "U.S.A",
                "region": "ASIAPAC"
            }, {
                "id": 23,
                "name": "CATOR01",
                "label": "Site 1",
                "location": "Toronto,Canada",
                "country": "Canada",
                "region": "EUROPE"
            }, {
                "id": 25,
                "name": "CATOR01",
                "label": "Site 1",
                "location": "Toronto,Canada",
                "country": "Canada",
                "region": "OCEANIA"
            }],  # available agents
            [{
                "id": 52,
                "name": "unit.tests.:www.dynamic:A:two-1.2.3.4"
            }],  # initial checks
            {
                "type": 'TCP'
            },  # check type
            {
                "id": 52906,
                "name": "unit.tests.:www.dynamic:A:two-1.2.3.4"
            },
            {
                "id": 52907,
                "name": "unit.tests.:www.dynamic:A:two-1.2.3.5"
            }
        ]

        plan = provider.plan(self.expected_healthcheck)

        # No root NS, no ignored, no excluded, no unsupported
        n = len(self.expected_healthcheck.records) - 8
        self.assertEqual(n, len(plan.changes))
        self.assertEqual(n, provider.apply(plan))

        provider._client._request.assert_has_calls([
            # get all domains to build the cache
            call('GET', '/domains'),
            # created the domain
            call('POST', '/domains', data={'names': ['unit.tests']})
        ])

        # Check we tried to get our pool
        provider._client._request.assert_has_calls([
            # get all pools to build the cache
            call('GET', '/pools/A'),
            # created the pool
            call('POST', '/pools/A', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "1.2.3.4",
                    "weight": 1,
                    "checkId": 52906,
                    "policy": 'followsonar'
                }, {
                    "value": "1.2.3.5",
                    "weight": 1,
                    "checkId": 52907,
                    "policy": 'followsonar'
                }]
            })
        ])

        # These two checks are broken up so that ordering doesn't break things.
        # Python3 doesn't make the calls in a consistent order so different
        # things follow the GET / on different runs
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/SRV', data={
                'roundRobin': [{
                    'priority': 10,
                    'weight': 20,
                    'value': 'foo-1.unit.tests.',
                    'port': 30
                }, {
                    'priority': 12,
                    'weight': 20,
                    'value': 'foo-2.unit.tests.',
                    'port': 30
                }],
                'name': '_srv._tcp',
                'ttl': 600,
            }),
        ])

        self.assertEqual(22, provider._client._request.call_count)

        provider._client._request.reset_mock()

        provider._client.records = Mock(return_value=[
            {
                'id': 11189897,
                'type': 'A',
                'name': 'www',
                'ttl': 300,
                'recordOption': 'roundRobin',
                'value': [
                    '1.2.3.4',
                    '2.2.3.4',
                ]
            }, {
                'id': 11189898,
                'type': 'A',
                'name': 'ttl',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [
                    '3.2.3.4'
                ]
            },  {
                'id': 11189899,
                'type': 'ALIAS',
                'name': 'alias',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [{
                    'value': 'aname.unit.tests.'
                }]
            }, {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": None,
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                },
                {
                    "value": "1.2.3.5",
                    "weight": 1
                }
            ]
        }])

        # Domain exists, we don't care about return
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:one"
            }]  # pool created in apply
        ]

        wanted = Zone('unit.tests.', [])
        wanted.add_record(Record.new(wanted, 'ttl', {
            'ttl': 300,
            'type': 'A',
            'value': '3.2.3.4'
        }))

        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
        }))

        plan = provider.plan(wanted)
        self.assertEqual(4, len(plan.changes))
        self.assertEqual(4, provider.apply(plan))

        # recreate for update, and deletes for the 2 parts of the other
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/A', data={
                'roundRobin': [{
                    'value': '3.2.3.4'
                }],
                'name': 'ttl',
                'ttl': 300
            }),
            call('PUT', '/pools/A/1808521', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "1.2.3.4",
                    "weight": 1
                }],
                'id': 1808521,
                'geofilter': 1
            }),
            call('DELETE', '/domains/123123/records/A/11189897'),
            call('DELETE', '/domains/123123/records/A/11189898'),
            call('DELETE', '/domains/123123/records/ANAME/11189899'),
        ], any_order=True)

    def test_apply_healthcheck_world(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        resp = Mock()
        resp.json = Mock()
        provider._client._request = Mock(return_value=resp)

        # non-existent domain, create everything
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808520,
                "name": "unit.tests.:www.dynamic:A:two",
            }]   # pool created in apply
        ]

        sonar_resp = Mock()
        sonar_resp.json = Mock()
        type(sonar_resp).headers = PropertyMock(return_value={
            "Location": "http://api.sonar.constellix.com/rest/api/tcp/52906"
        })
        sonar_resp.headers = Mock()
        provider._sonar._request = Mock(return_value=sonar_resp)

        sonar_resp.json.side_effect = [
            [{
                "id": 1,
                "name": "USWAS01",
                "label": "Site 1",
                "location": "Washington, DC, U.S.A",
                "country": "U.S.A",
                "region": "ASIAPAC"
            }, {
                "id": 23,
                "name": "CATOR01",
                "label": "Site 1",
                "location": "Toronto,Canada",
                "country": "Canada",
                "region": "EUROPE"
            }],  # available agents
            [],  # no checks
            {
                "id": 52906,
                "name": "check1"
            },
            {
                "id": 52907,
                "name": "check2"
            }
        ]

        plan = provider.plan(self.expected_healthcheck_world)

        # No root NS, no ignored, no excluded, no unsupported
        n = len(self.expected_healthcheck.records) - 8
        self.assertEqual(n, len(plan.changes))
        self.assertEqual(n, provider.apply(plan))

        provider._client._request.assert_has_calls([
            # get all domains to build the cache
            call('GET', '/domains'),
            # created the domain
            call('POST', '/domains', data={'names': ['unit.tests']})
        ])

        # Check we tried to get our pool
        provider._client._request.assert_has_calls([
            # get all pools to build the cache
            call('GET', '/pools/AAAA'),
            # created the pool
            call('POST', '/pools/AAAA', data={
                'name': 'unit.tests.:www.dynamic:AAAA:two',
                'type': 'AAAA',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "2601:642:500:e210:62f8:1dff:feb8:947a",
                    "weight": 1,
                    "checkId": 52906,
                    "policy": 'followsonar'
                }, {
                    "value": "2601:644:500:e210:62f8:1dff:feb8:947a",
                    "weight": 1,
                    "checkId": 52907,
                    "policy": 'followsonar'
                }]
            })
        ])

        # These two checks are broken up so that ordering doesn't break things.
        # Python3 doesn't make the calls in a consistent order so different
        # things follow the GET / on different runs
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/SRV', data={
                'roundRobin': [{
                    'priority': 10,
                    'weight': 20,
                    'value': 'foo-1.unit.tests.',
                    'port': 30
                }, {
                    'priority': 12,
                    'weight': 20,
                    'value': 'foo-2.unit.tests.',
                    'port': 30
                }],
                'name': '_srv._tcp',
                'ttl': 600,
            }),
        ])

        self.assertEqual(22, provider._client._request.call_count)

        provider._client._request.reset_mock()

        provider._client.records = Mock(return_value=[
            {
                'id': 11189897,
                'type': 'A',
                'name': 'www',
                'ttl': 300,
                'recordOption': 'roundRobin',
                'value': [
                    '1.2.3.4',
                    '2.2.3.4',
                ]
            }, {
                'id': 11189898,
                'type': 'A',
                'name': 'ttl',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [
                    '3.2.3.4'
                ]
            },  {
                'id': 11189899,
                'type': 'ALIAS',
                'name': 'alias',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [{
                    'value': 'aname.unit.tests.'
                }]
            }, {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": None,
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                },
                {
                    "value": "1.2.3.5",
                    "weight": 1
                }
            ]
        }])

        # Domain exists, we don't care about return
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:one"
            }]  # pool created in apply
        ]

        wanted = Zone('unit.tests.', [])
        wanted.add_record(Record.new(wanted, 'ttl', {
            'ttl': 300,
            'type': 'A',
            'value': '3.2.3.4'
        }))

        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
        }))

        plan = provider.plan(wanted)
        self.assertEqual(4, len(plan.changes))
        self.assertEqual(4, provider.apply(plan))

        # recreate for update, and deletes for the 2 parts of the other
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/A', data={
                'roundRobin': [{
                    'value': '3.2.3.4'
                }],
                'name': 'ttl',
                'ttl': 300
            }),
            call('PUT', '/pools/A/1808521', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    "value": "1.2.3.4",
                    "weight": 1
                }],
                'id': 1808521,
                'geofilter': 1
            }),
            call('DELETE', '/domains/123123/records/A/11189897'),
            call('DELETE', '/domains/123123/records/A/11189898'),
            call('DELETE', '/domains/123123/records/ANAME/11189899'),
        ], any_order=True)

    def test_apply_dynamic(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        resp = Mock()
        resp.json = Mock()
        provider._client._request = Mock(return_value=resp)

        # non-existent domain, create everything
        resp.json.side_effect = [
            [],  # no domains returned during populate
            [{
                'id': 123123,
                'name': 'unit.tests'
            }],  # domain created in apply
            [],  # No pools returned during populate
            [{
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:one"
            }],  # pool created in apply
            [],  # no geofilters returned during populate
            [{
                "id": 5303,
                "name": "unit.tests.:www.dynamic:A:one",
                "filterRulesLimit": 100,
                "geoipContinents": ["AS", "OC"],
                "geoipCountries": ["ES", "SE", "UA"],
                "regions": [
                    {
                        "continentCode": "NA",
                        "countryCode": "CA",
                        "regionCode": "NL"
                    }
                ]
            }],  # geofilters created in applly
            [{
                "id": 1808520,
                "name": "unit.tests.:www.dynamic:A:two",
            }],  # pool created in apply
            {
                'id': 123123,
                'name': 'unit.tests',
                'hasGeoIP': False
            },  # domain listed for enabling geo
            []  # enabling geo
        ]

        plan = provider.plan(self.expected_dynamic)

        # No ignored, no excluded, no unsupported
        n = len(self.expected_dynamic.records) - 7
        self.assertEqual(n, len(plan.changes))
        self.assertEqual(n, provider.apply(plan))

        provider._client._request.assert_has_calls([
            # get all domains to build the cache
            call('GET', '/domains'),
            # created the domain
            call('POST', '/domains', data={'names': ['unit.tests']})
        ])
#
        # Check we tried to get our pool
        provider._client._request.assert_has_calls([
            call('GET', '/pools/A'),
            call('POST', '/pools/A', data={
                'name': 'unit.tests.:www.dynamic:A:one',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    'value': '1.2.3.6',
                    'weight': 1
                }, {
                    'value': '1.2.3.7',
                    'weight': 1}]
            }),
            call('GET', '/geoFilters'),
            call('POST', '/geoFilters', data={
                'filterRulesLimit': 100,
                'name': 'unit.tests.:www.dynamic:A:one',
                'geoipContinents': ['AS', 'OC'],
                'geoipCountries': ['ES', 'SE', 'UA'],
                'regions': [{
                    'continentCode': 'NA',
                    'countryCode': 'CA',
                    'regionCode': 'NL'}]
            }),
            call('POST', '/pools/A', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{
                    'value': '1.2.3.4',
                    'weight': 1
                }, {
                    'value': '1.2.3.5',
                    'weight': 1}]
            })
        ])

        # These two checks are broken up so that ordering doesn't break things.
        # Python3 doesn't make the calls in a consistent order so different
        # things follow the GET / on different runs
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/SRV', data={
                'roundRobin': [{
                    'priority': 10,
                    'weight': 20,
                    'value': 'foo-1.unit.tests.',
                    'port': 30
                }, {
                    'priority': 12,
                    'weight': 20,
                    'value': 'foo-2.unit.tests.',
                    'port': 30
                }],
                'name': '_srv._tcp',
                'ttl': 600,
            }),
        ])

        self.assertEqual(28, provider._client._request.call_count)

        provider._client._request.reset_mock()

        provider._client.records = Mock(return_value=[
            {
                'id': 11189897,
                'type': 'A',
                'name': 'www',
                'ttl': 300,
                'recordOption': 'roundRobin',
                'value': [
                    '1.2.3.4',
                    '2.2.3.4',
                ]
            }, {
                'id': 11189898,
                'type': 'A',
                'name': 'ttl',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [
                    '3.2.3.4'
                ]
            }, {
                'id': 11189899,
                'type': 'ALIAS',
                'name': 'alias',
                'ttl': 600,
                'recordOption': 'roundRobin',
                'value': [{
                    'value': 'aname.unit.tests.'
                }]
            }, {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": {
                    "geoipFilter": 1
                },
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }, {
                "id": 1808521,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": {
                    "geoipFilter": 5303
                },
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808522
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[
            {
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:two",
                "type": "A",
                "values": [
                    {
                        "value": "1.2.3.4",
                        "weight": 1
                    },
                    {
                        "value": "1.2.3.5",
                        "weight": 1
                    }
                ]
            },
            {
                "id": 1808522,
                "name": "unit.tests.:www.dynamic:A:one",
                "type": "A",
                "values": [
                    {
                        "value": "1.2.3.6",
                        "weight": 1
                    },
                    {
                        "value": "1.2.3.7",
                        "weight": 1
                    }
                ]
            }
        ])

        provider._client.geofilters = Mock(return_value=[
            {
                "id": 5303,
                "name": "unit.tests.:www.dynamic:A:one",
                "filterRulesLimit": 100,
                "geoipContinents": ["AS", "OC"],
                "geoipCountries": ["ES", "SE", "UA"],
                "regions": [
                    {
                        "continentCode": "NA",
                        "countryCode": "CA",
                        "regionCode": "NL"
                    }
                ]
            }
        ])

        # Domain exists, we don't care about return
        resp.json.side_effect = [
            [],
            [],
            [],
            [],
            {
                'id': 123123,
                'name': 'unit.tests',
                'hasGeoIP': True
            }  # domain listed for enabling geo
        ]

        wanted = Zone('unit.tests.', [])
        wanted.add_record(Record.new(wanted, 'ttl', {
            'ttl': 300,
            'type': 'A',
            'value': '3.2.3.4'
        }))

        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'one': {
                        'fallback': 'two',
                        'values': [{
                            'value': '1.2.3.6',
                            'weight': 1
                        }, {
                            'value': '1.2.3.7',
                            'weight': 1
                        }],
                    },
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'geos': [
                        'AS',
                        'EU-ES',
                        'EU-UA',
                        'EU-SE',
                        'NA-CA-NL',
                        'OC'
                    ],
                    'pool': 'one'
                }, {
                    'pool': 'two',
                }],
            },
        }))

        plan = provider.plan(wanted)
        self.assertEqual(4, len(plan.changes))
        self.assertEqual(4, provider.apply(plan))

        # recreate for update, and deletes for the 2 parts of the other
        provider._client._request.assert_has_calls([
            call('POST', '/domains/123123/records/A', data={
                'roundRobin': [{
                    'value': '3.2.3.4'
                }],
                'name': 'ttl',
                'ttl': 300
            }),

            call('DELETE', '/domains/123123/records/A/1808521'),
            call('DELETE', '/geoFilters/5303'),
            call('DELETE', '/pools/A/1808522'),
            call('DELETE', '/domains/123123/records/A/1808520'),
            call('DELETE', '/pools/A/1808521'),
            call('DELETE', '/domains/123123/records/ANAME/11189899'),

            call('PUT', '/pools/A/1808522', data={
                'name': 'unit.tests.:www.dynamic:A:one',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [
                    {'value': '1.2.3.6', 'weight': 1},
                    {'value': '1.2.3.7', 'weight': 1}],
                'id': 1808522,
                'geofilter': 5303
            }),

            call('PUT', '/geoFilters/5303', data={
                'filterRulesLimit': 100,
                'name': 'unit.tests.:www.dynamic:A:one',
                'geoipContinents': ['AS', 'OC'],
                'geoipCountries': ['ES', 'SE', 'UA'],
                'regions': [{
                    'continentCode': 'NA',
                    'countryCode': 'CA',
                    'regionCode': 'NL'}],
                'id': 5303
            }),

            call('PUT', '/pools/A/1808521', data={
                'name': 'unit.tests.:www.dynamic:A:two',
                'type': 'A',
                'numReturn': 1,
                'minAvailableFailover': 1,
                'ttl': 300,
                'values': [{'value': '1.2.3.4', 'weight': 1}],
                'id': 1808521,
                'geofilter': 1
            }),

            call('GET', '/domains/123123'),
            call('POST', '/domains/123123/records/A', data={
                'name': 'www.dynamic',
                'ttl': 300,
                'pools': [1808522],
                'recordOption': 'pools',
                'geolocation': {
                    'geoipUserRegion': [5303]
                }
            }),

            call('POST', '/domains/123123/records/A', data={
                'name': 'www.dynamic',
                'ttl': 300,
                'pools': [1808522],
                'recordOption': 'pools',
                'geolocation': {
                    'geoipUserRegion': [5303]
                }
            })
        ], any_order=True)

    def test_dynamic_record_failures(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        resp = Mock()
        resp.json = Mock()
        provider._client._request = Mock(return_value=resp)

        # Let's handle some failures for pools - first if it's not a simple
        # weighted pool - we'll be OK as we assume a weight of 1 for all
        # entries
        provider._client._request.reset_mock()
        provider._client.records = Mock(return_value=[
            {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": None,
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                }
            ]
        }])

        provider._client.geofilters = Mock(return_value=[])

        wanted = Zone('unit.tests.', [])

        resp.json.side_effect = [
            ['{}'],
            ['{}'],
        ]
        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'two': {
                        'values': [{
                            'value': '1.2.3.4'
                        }],
                    },
                },
                'rules': [{
                    'pool': 'two',
                }],
            },
        }))

        plan = provider.plan(wanted)
        self.assertIsNone(plan)

    def test_dynamic_record_updates(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        # Constellix API can return an error if you try and update a pool and
        # don't change anything, so let's test we handle it silently

        provider._client.records = Mock(return_value=[
            {
                "id": 1808520,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": {
                    "geoipFilter": 1
                },
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808521
                ]
            }, {
                "id": 1808521,
                "type": "A",
                "name": "www.dynamic",
                "geolocation": {
                    "geoipFilter": 5303
                },
                "recordOption": "pools",
                "ttl": 300,
                "value": [],
                "pools": [
                    1808522
                ]
            }
        ])

        provider._client.pools = Mock(return_value=[
            {
                "id": 1808521,
                "name": "unit.tests.:www.dynamic:A:two",
                "type": "A",
                "values": [
                    {
                        "value": "1.2.3.4",
                        "weight": 1
                    },
                    {
                        "value": "1.2.3.5",
                        "weight": 1
                    }
                ]
            },
            {
                "id": 1808522,
                "name": "unit.tests.:www.dynamic:A:one",
                "type": "A",
                "values": [
                    {
                        "value": "1.2.3.6",
                        "weight": 1
                    },
                    {
                        "value": "1.2.3.7",
                        "weight": 1
                    }
                ]
            }
        ])

        provider._client.geofilters = Mock(return_value=[
            {
                "id": 6303,
                "name": "some.other",
                "filterRulesLimit": 100,
                "createdTs": "2021-08-19T14:47:47Z",
                "modifiedTs": "2021-08-19T14:47:47Z",
                "geoipContinents": ["AS", "OC"],
                "geoipCountries": ["ES", "SE", "UA"],
                "regions": [
                    {
                        "continentCode": "NA",
                        "countryCode": "CA",
                        "regionCode": "NL"
                    }
                ]
            }, {
                "id": 5303,
                "name": "unit.tests.:www.dynamic:A:one",
                "filterRulesLimit": 100,
                "geoipContinents": ["AS", "OC"],
                "geoipCountries": ["ES", "SE", "UA"],
                "regions": [
                    {
                        "continentCode": "NA",
                        "countryCode": "CA",
                        "regionCode": "NL"
                    }
                ]
            }
        ])

        wanted = Zone('unit.tests.', [])

        wanted.add_record(Record.new(wanted, 'www.dynamic', {
            'ttl': 300,
            'type': 'A',
            'values': [
                '1.2.3.4'
            ],
            'dynamic': {
                'pools': {
                    'one': {
                        'fallback': 'two',
                        'values': [{
                            'value': '1.2.3.6',
                            'weight': 1
                        }, {
                            'value': '1.2.3.7',
                            'weight': 1
                        }],
                    },
                    'two': {
                        'values': [{
                            'value': '1.2.3.4',
                            'weight': 1
                        }],
                    },
                },
                'rules': [{
                    'geos': [
                        'AS',
                        'EU-ES',
                        'EU-UA',
                        'EU-SE',
                        'OC'
                    ],
                    'pool': 'one'
                }, {
                    'pool': 'two',
                }],
            },
        }))

        # Try an error we can handle
        with requests_mock() as mock:
            mock.get(
                "https://api.dns.constellix.com/v1/domains",
                status_code=200,
                text='[{"id": 1234, "name": "unit.tests", "hasGeoIP": true}]')
            mock.get(
                "https://api.dns.constellix.com/v1/domains/1234",
                status_code=200,
                text='{"id": 1234, "name": "unit.tests", "hasGeoIP": true}')
            mock.delete(ANY, status_code=200,
                        text='{}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808521",
                     status_code=400,
                     text='{"errors": [\"no changes to save\"]}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808522",
                     status_code=400,
                     text='{"errors": [\"no changes to save\"]}')
            mock.put("https://api.dns.constellix.com/v1/geoFilters/5303",
                     status_code=400,
                     text='{"errors": [\"no changes to save\"]}')
            mock.post(ANY, status_code=200,
                      text='[{"id": 1234}]')

            plan = provider.plan(wanted)
            self.assertEqual(1, len(plan.changes))
            self.assertEqual(1, provider.apply(plan))

            provider._client.geofilters = Mock(return_value=[
                {
                    "id": 5303,
                    "name": "unit.tests.:www.dynamic:A:one",
                    "filterRulesLimit": 100,
                    "regions": [
                        {
                            "continentCode": "NA",
                            "countryCode": "CA",
                            "regionCode": "NL"
                        }
                    ]
                }
            ])

            plan = provider.plan(wanted)
            self.assertEqual(1, len(plan.changes))
            self.assertEqual(1, provider.apply(plan))

            provider._client.geofilters = Mock(return_value=[
                {
                    "id": 5303,
                    "name": "unit.tests.:www.dynamic:A:one",
                    "filterRulesLimit": 100,
                    "geoipContinents": ["AS", "OC"],
                }
            ])

            plan = provider.plan(wanted)
            self.assertEqual(1, len(plan.changes))
            self.assertEqual(1, provider.apply(plan))

        # Now what happens if an error happens that we can't handle
        # geofilter case
        with requests_mock() as mock:
            mock.get(
                "https://api.dns.constellix.com/v1/domains",
                status_code=200,
                text='[{"id": 1234, "name": "unit.tests", "hasGeoIP": true}]')
            mock.get(
                "https://api.dns.constellix.com/v1/domains/1234",
                status_code=200,
                text='{"id": 1234, "name": "unit.tests", "hasGeoIP": true}')
            mock.delete(ANY, status_code=200,
                        text='{}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808521",
                     status_code=400,
                     text='{"errors": [\"no changes to save\"]}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808522",
                     status_code=400,
                     text='{"errors": [\"no changes to save\"]}')
            mock.put("https://api.dns.constellix.com/v1/geoFilters/5303",
                     status_code=400,
                     text='{"errors": [\"generic error\"]}')
            mock.post(ANY, status_code=200,
                      text='[{"id": 1234}]')

            plan = provider.plan(wanted)
            self.assertEqual(1, len(plan.changes))
            with self.assertRaises(ConstellixClientBadRequest):
                provider.apply(plan)

        # Now what happens if an error happens that we can't handle
        with requests_mock() as mock:
            mock.get(
                "https://api.dns.constellix.com/v1/domains",
                status_code=200,
                text='[{"id": 1234, "name": "unit.tests", "hasGeoIP": true}]')
            mock.get(
                "https://api.dns.constellix.com/v1/domains/1234",
                status_code=200,
                text='{"id": 1234, "name": "unit.tests", "hasGeoIP": true}')
            mock.delete(ANY, status_code=200,
                        text='{}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808521",
                     status_code=400,
                     text='{"errors": [\"generic error\"]}')
            mock.put("https://api.dns.constellix.com/v1/pools/A/1808522",
                     status_code=400,
                     text='{"errors": [\"generic error\"]}')
            mock.put("https://api.dns.constellix.com/v1/geoFilters/5303",
                     status_code=400,
                     text='{"errors": [\"generic error\"]}')
            mock.post(ANY, status_code=200,
                      text='[{"id": 1234}]')

            plan = provider.plan(wanted)
            self.assertEqual(1, len(plan.changes))
            with self.assertRaises(ConstellixClientBadRequest):
                provider.apply(plan)

    def test_pools_that_are_notfound(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                }
            ]
        }])

        self.assertIsNone(provider._client.pool_by_id('A', 1))
        self.assertIsNone(provider._client.pool('A', 'foobar'))

    def test_pools_are_cached_correctly(self):
        provider = ConstellixProvider('test', 'api', 'secret')

        provider._client.pools = Mock(return_value=[{
            "id": 1808521,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                }
            ]
        }])

        found = provider._client.pool('A', 'unit.tests.:www.dynamic:A:two')
        self.assertIsNotNone(found)

        not_found = provider._client.pool('AAAA',
                                          'unit.tests.:www.dynamic:A:two')
        self.assertIsNone(not_found)

        provider._client.pools = Mock(return_value=[{
            "id": 42,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "A",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                }
            ]
        }, {
            "id": 451,
            "name": "unit.tests.:www.dynamic:A:two",
            "type": "AAAA",
            "values": [
                {
                    "value": "1.2.3.4",
                    "weight": 1
                }
            ]
        }])

        a_pool = provider._client.pool('A', 'unit.tests.:www.dynamic:A:two')
        self.assertEqual(42, a_pool['id'])

        aaaa_pool = provider._client.pool('AAAA',
                                          'unit.tests.:www.dynamic:A:two')
        self.assertEqual(451, aaaa_pool['id'])
