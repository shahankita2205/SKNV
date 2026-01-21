curl -XPOST -u rcook-ion-test:qwer1234 -d \
'{
"event" : "script.message.received",
"method" : "POST",
"headers" : {"System-Key" : "e5fcbbc9-d349-4164-811d-8d99397a9bb2", "Data-ID" : "92de3976-b42e-4248-82ca-9c01379b302c"},
"payload" : {
"external_client_identifier" : "590e4bb1-67c8-4e9f-a230-9d592172ba04"
},
"endpoint" : "https://api.ryan.sknv.cubby.zone/hooks/new-script-received",
"identifier" : "590e4bb1-67c8-4e9f-a230-9d592172ba04",
"registration_status" : 1,
"on_failure_email": "rcook@sknv.com",
"originate_from_local" : 0
}' "https://testsknv.pharmetika.com/api/interface/v5/webhook/id/590e4bb1-67c8-4e9f-a230-9d592172ba04";
