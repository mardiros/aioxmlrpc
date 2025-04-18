import pytest
from aioxmlrpc.server import SimpleXMLRPCDispatcher


RPC_CALL = """<?xml version='1.0'?>
<methodCall>
    <methodName>division</methodName>
    <params>
        <param><value><int>{0}</int></value></param>
        <param><value><int>{1}</int></value></param>
    </params>
</methodCall>
"""


RPC_RESPONSE = """<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><double>{0}</double></value>
</param>
</params>
</methodResponse>
"""

RPC_FAULT = """<?xml version='1.0'?>
<methodResponse>
<fault>
<value><struct>
<member>
<name>faultCode</name>
<value><int>1</int></value>
</member>
<member>
<name>faultString</name>
<value><string>{0}</string></value>
</member>
</struct></value>
</fault>
</methodResponse>
"""


async def test_marshall_unregister():
    d = SimpleXMLRPCDispatcher()
    resp = await d._marshaled_dispatch(RPC_CALL.format(8, 2))
    assert resp.decode() == RPC_FAULT.format(
        "&lt;class 'Exception'&gt;:method \"division\" is not supported"
    )


@pytest.mark.parametrize(
    "params,expected",
    [
        pytest.param(RPC_CALL.format(8, 2), RPC_RESPONSE.format("4.0"), id="ok"),
        pytest.param(
            RPC_CALL.format(8, 0),
            RPC_FAULT.format("&lt;class 'ZeroDivisionError'&gt;:division by zero"),
            id="fault",
        ),
    ],
)
async def test_marshall(params: str, expected: str):
    d = SimpleXMLRPCDispatcher()
    d.register_function(lambda x, y: x / y, "division")
    resp = await d._marshaled_dispatch(params)
    assert resp.decode() == expected


async def test_multicall():
    d = SimpleXMLRPCDispatcher()
    d.register_function(lambda x, y: x / y, "division")
    resp = await d.system_multicall(
        [
            {"methodName": "division", "params": [8, 2]},
            {"methodName": "division", "params": [8, 0]},
        ],
    )
    assert resp == [
        [
            4.0,
        ],
        {
            "faultCode": 1,
            "faultString": "ZeroDivisionError:division by zero",
        },
    ]
