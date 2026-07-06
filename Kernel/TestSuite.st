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
		self test3.
		self test4.
		self test5.
		self test6.
		self test7.
		self test8.
		self test9
	]
	
	test1 [
		"test1"
		testInst1 isNil; notNil; isInteger; isNil.
		true size; basicSize
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
	
	test6 [
		"test6"
		| a b c |
		a := #[5 6 7 100].
		b := #([1 2 3] [8 9 10 11 23]).
		c := #(('abc' 'xyz') (1 2 9 7 3 19) 20).
		^ #(1 2 3 'hello' false true nil #new)
	]
	
	test7 [
		"test7"
		| x y z |
		z := SmallInteger largest.
		y := z bitShift: -30.
		x := ((16r10FF bitAnd: 16rB010) bitOr: 32) bitXor: 33.
		x := 139302 quo: -234.
		z := 1229 // 14.
		y := 1229 \\ 14.
		y := 1000 * 4 * 2.
		x := 1 + 2 - 100 + 105.
		x < 4000 and: [x > 2].
		x >= 0 and: [x <= 8].
		^x = 8 and: [x ~= 12359303]
	]
	
	test8 [
		"test8"
		^24 gcd: 32
	]
	
	test9 [
		"test9"
		| a |
		a := #(1 2 3 4 5).
		a at: 1; at: 2; at: 5.
		a at: 2 put: 10.
		a at: 3 put: 11.
		a at: 2; at: 3
	]
]