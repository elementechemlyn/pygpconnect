import pytest
import pygpconnect
import logging
import jwt

def logassert(test,msg):
    if not test:
        logging.error(msg)
        assert test,msg
    
def test_getendpoint():
    conn = pygpconnect.GPConnect()
    json_resp = conn.getEndPoint()
    logassert("issue" not in json_resp,json_resp)

def test_getPatient():
    conn = pygpconnect.GPConnect()
    conn.getEndPoint()
    pat_json = conn.getPatient()
    logassert("issue" not in pat_json,pat_json)

def test_getAppointments():
    conn = pygpconnect.GPConnect()
    conn.getEndPoint()
    pat_json = conn.getPatient()
    logassert("issue" not in pat_json,pat_json)
    logassert("entry" in pat_json,pat_json)
    pat_id = pat_json["entry"][0]["resource"]["id"]
    apt_json = conn.getAppointments(pat_id)
    logassert("issue" not in apt_json,apt_json)

def test_getCareRecord():
    conn = pygpconnect.GPConnect()
    conn.getEndPoint()
    record_json = conn.getCareRecord()
    logassert("issue" not in record_json,record_json)
    
def test_makejwt():
    conn = pygpconnect.GPConnect()
    token = conn.makeJWT("patient","read","patient-id")
    token = jwt.decode(token,"123456",verify=False)
