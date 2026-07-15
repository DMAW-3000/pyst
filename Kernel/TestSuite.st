"======================================================================
|
|   pyst tests
|
|
 ======================================================================"
 
 Object subclass: TestSuite [
	| testInst1 testInst2 |
	
	TestClassVar := nil.
	
	TestSuite class >> testClassVar [
		^TestClassVar
	]
	
	TestSuite class >> testClassVar: val [
		TestClassVar := val
	]
	
	runAll [
		"Run all of the tests"
		self 	test1;
				test2;
				test3;
				test4;
				test5;
				test6;
				test7;
				test8;
				test9;
				test10;
				test11
	]
	
	test1 [
		"test1"
		| a1 a2 |
		a1 := #(1 2 3) copy.
		a2 := #(4 5 6) copy.
		a2 become: a1.
		a2 at: 1.
		a1 at: 1.
		testInst1 isNil; notNil; isInteger; isNil.
		true size; basicSize.
		(ByteArray new: 20) size; basicSize.
		(Array new: 10) size; basicSize
	]
	
	test2 [
		"test2"
		| d e |
		(d := $A asLowercase) isUppercase.
		(e := $b asUppercase) isUppercase.
		d := FinalizableObjects.
		e := Object dependencies.
		TestSuite testClassVar: #(10 20 30).
		TestSuite testClassVar.
		KernelInitialized ifFalse: [KernelInitialized := true].
		^true isKindOf: false class
	]
 
	test3 [
        "test3"
		Collection isReadOnly.
		(Array new: 1) isReadOnly.
		#testSym size.
		'test string' size.
		[:x | true and: [x]] value: false.
		[:x | true and: [x]] cull: false cull:false.
		[:x :y :z | x + y - z ] valueWithArguments: #(5 22 7)
    ]
	
	test4 [
		"test4"
		| x y |
		x := WriteStream on: (Array new: 2).
		x nextPutAll: 'This is a test write string'.
		x := ReadStream on: 'this is a test string'.
		21 timesRepeat: [x next].
		x := y := false.
		(x := y := true) isNil.
		(x := false) ifFalse: [	x := true ]
	]
	
	test5 [
		"test5"
		super isNil; notNil; isNil.
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
		| a b |
		a := #(1 2 3 4 5).
		b := a copy.
		$N = $r. $X = $X.
		b at: 1; at: 2; at: 5.
		a at: 2 put: 10.
		a at: 3 put: 11.
		a at: 2; at: 3
	]
	
	test10 [
		"test10"
		| a |
		testInst1 ifNil: [testInst1 := 1].
		testInst2 ifNil: [testInst2 := 'test instance variable'].
		testInst2 size. self isNil.
		(a := Array new: 6 withAll: 10328) at: 2
	]
	
	test11 [
		"test11"
		| x y |
		x := Array basicNew: 3.
		y := Array basicNew: 2.
		x at: 1 put: y.
		y allOwners.
		Exception new
	]
]