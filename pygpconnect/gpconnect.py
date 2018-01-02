import requests
import jwt
import datetime
import json
import uuid

base_url = "http://ec2-54-194-109-184.eu-west-1.compute.amazonaws.com"

class GPConnect(object):

    def __init__(self):
        self.SspFrom = "200000000359"
        self.SspTo = None
        self.endpoint = None
        self.headers = {"Accept":"application/json+fhir","Ssp-From":"200000000359"}

    def makeHeaders(self,interaction,identifer,scope="patient",operation="read"):
        self.headers['Ssp-InteractionID'] = interaction
        self.headers['Authorization'] = 'Bearer %s' % self.makeJWT(scope,operation,identifer)
        self.headers['Ssp-TraceID'] = str(uuid.uuid4())
        self.headers['Content-Type'] = "application/json+fhir"
        
    def getEndPoint(self,ods="GPC001",interaction="urn:nhs:names:services:gpconnect:fhir:rest:search:patient"):

        url = "%s/api/ldap/endpointLookup?odsCode=%s&interactionId=%s" % (base_url,ods,interaction)
        r = requests.get(url)
        end_point =  json.loads(r.text)
        self.SspTo = end_point["recievingSysASID"]
        self.endpoint = "%s%s" % (base_url,end_point["endpointURL"],)
        self.headers['Ssp-To'] = self.SspTo
        return r.json()

    def getPatient(self,nhsnumber="9476719931"):
        identifier = "https://fhir.nhs.uk/Id/nhs-number|%s" % (nhsnumber,)
        url = "%s/Patient?identifier=%s" % (self.endpoint,identifier)
        self.makeHeaders('urn:nhs:names:services:gpconnect:fhir:rest:search:patient',nhsnumber)
        r = requests.get(url,headers=self.headers)
        return r.json()
        
    def getAppointments(self,patientid="4",nhsnumber="9476719931"):      
        url = "%s/Patient/%s/Appointment" % (self.endpoint,patientid,)
        self.makeHeaders('urn:nhs:names:services:gpconnect:fhir:rest:search:patient_appointments',nhsnumber)
        r = requests.get(url,headers=self.headers)
        return r.json()
        
    def getCareRecord(self,nhsnumber="9476719931",fromDate="2015",toDate="2016",recordSelection="SUM"):
        identifier = "https://fhir.nhs.uk/Id/nhs-number|%s" % (nhsnumber,)
        body = {"resourceType" : "Parameters",
                "parameter" : [ {"name" : "patientNHSNumber", "valueIdentifier" :
                                 { "system" : "https://fhir.nhs.uk/Id/nhs-number","value" : nhsnumber }},
                                {"name" : "recordSection","valueCodeableConcept" :
                                 { "coding": [
                                     {"system":"http://fhir.nhs.net/ValueSet/gpconnect-record-section-1","code":"SUM","display":"Summary"}]} },
                            ]
                }
        url = "%s/Patient/$gpc.getcarerecord" % (self.endpoint,)
        self.makeHeaders('urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord',nhsnumber)
        data = {}
        r = requests.post(url,json.dumps(body),headers=self.headers)
        return r.json()
        
    def makeJWT(self, scope, operation, identifier):
        
        #Lifted "as is" from https://github.com/nhs-digital/gpconnect-demonstrator/blob/master/webapp/app/scripts/tenant/gpconnect/fhirJWT.js
        header = {"alg": 'none', "typ": 'JWT'}
        #Payload
        payload = {}
        now = datetime.datetime.utcnow()
        end = now + datetime.timedelta(minutes=5)
        payload["iss"] = __name__
        payload["sub"] = "1" # Dummy user as we don't have a login so all users are the same
        payload["aud"] = "https://authorize.fhir.nhs.net/token"
        payload["exp"] = end;
        payload["iat"] = now
        payload["reason_for_request"] = "directcare"

        if scope.index("patient") > -1:
            payload["requested_record"] = {
                "resourceType": "Patient",
                "identifier": [{
                        "system": "https://fhir.nhs.uk/Id/nhs-number",
                        "value": identifier
                    }]
            }
            payload["requested_scope"] = "patient/*." + operation;
        else:
            payload["requested_record"] = {
                "resourceType": "Organization",
                "identifier": [{
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": identifier
                    }]
            }
            payload["requested_scope"] = "organization/*." + operation;

        payload["requesting_device"] = {
            "resourceType": "Device",
            "id": "1",
            "identifier": [{
                    "system": "Web Interface",
                    "value": "GP Connect Demonstrator"
                }],
            "model": "Demonstrator",
            "version": "1.0"
        }
        payload["requesting_organization"] = {
            "resourceType": "Organization",
            "id": "1",
            "identifier": [{
                    "system": "https://fhir.nhs.net/Id/ods-organization-code",
                    "value": "[ODSCode]"
                }],
            "name": "GP Connect Demonstrator"
        }
        payload["requesting_practitioner"] = {
            "resourceType": "Practitioner",
            "id": "1",
            "identifier": [{
                    "system": "https://fhir.nhs.net/sds-user-id",
                    "value": "G13579135"
                },
                {
                    "system": "localSystem",
                    "value": "1"
                }],
            "name": {
                "family": ["Demonstrator"],
                "given": ["GPConnect"],
                "prefix": ["Mr"]
            }
        }
        #Sign JWT, password=123456
        return jwt.encode(payload,"123456",headers=header)

