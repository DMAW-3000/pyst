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
		self test2.
		self test3
	]
	
	test1 [
		"test1"
		testInst1 isNil; notNil; isInteger; isNil
	]
	
	test2 [
		"test2"
		^true isKindOf: false class
	]
 
	test3 [
        "test3"
		^[:x | true and: [x]] value: false
    ]
]