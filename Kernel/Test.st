"======================================================================
|
|   pyst tests
|
|
 ======================================================================"
 
 Object subclass: Test [
	| testInst1 testInst2 |
 
	test1 [
        "test1"
		| b |
		b := nil.
		self ifNotNil: [b ifNil: [b := self]].
		^b
    ]
	
]