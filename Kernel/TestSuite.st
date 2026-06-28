"======================================================================
|
|   pyst tests
|
|
 ======================================================================"
 
 Object subclass: TestSuite [
	| testInst1 testInst2 |
	
	runAll [
		"Run all of the tests"
		self test1.
		self test2
	]
	
	test1 [
		"test1"
		^true isKindOf: false class
	]
 
	test2 [
        "test2"
		^[:x | true and: [x]] value: false
    ]
]