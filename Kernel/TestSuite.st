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
		self test5.
		self test1.
		self test2.
		self test3.
		self test4
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
	
	test4 [
		"test4"
		| x y |
		x := y := false.
		(x := y := true) isNil.
		(x := false) ifFalse: [	x := true ]
	]
	
	test5 [
		"test5"
		true ifTrue: [ | r s | r := false. s := true].
		[:a | | x | x := a] value: #nil
	]
]