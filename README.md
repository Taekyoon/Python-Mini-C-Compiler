# Python-Mini-C-Compiler
This project is to convert C version Mini-C Compiler into Python version for python love developers. 

## Prerequisites

```
Python 3.6
```

## Quick Start and Installation

These instructions will get you a copy of the project up and run on your 
local machine for development and testing purposes. See deployment for notes 
on how to deploy the project on a live system.

To get started, download this repository.
~~~ sh
$ git clone 
~~~

Run Compiler by main.py. You need to input .mc files to make 
~~~ sh
$ python main.py --path='<your mc code file path>' --save='<place your save file>'
~~~

This compiler can tested by .mc code files in test_codes folder, so you can test it by like this way.
~~~ sh
$ python main.py --path='./test_codes/perfect.mc' --save='./'
~~~

When you run main.py, you will get .ast, .uco files. 

And, here are the examples of .mc, .ast, .uco files

.mc file 
~~~
/*
A perfect number is an integer which is equal to the sum of all its divisors including 1 but excluding the number itself.
*/

const int max = 500;

void main()
{
	int i, j, k;
	int rem, sum; //rem : remainder
  .............
~~~

.ast file 
~~~
  Nonterminal: PROGRAM
       Nonterminal: DCL
            Nonterminal: DCL_SPEC
                 Nonterminal: CONST_NODE
                 Nonterminal: INT_NODE
            Nonterminal: DCL_ITEM
                 Nonterminal: SIMPLE_VAR
                      Terminal: max
                 Terminal: 500
       Nonterminal: FUNC_DEF
       ..........
~~~

.uco file 
~~~
main       fun 5 2 2
           sym 2 1 1
           sym 2 2 1
           sym 2 3 1
           sym 2 4 1
           sym 2 5 1
           ldc 2
           str 2 1
$$0        nop
           lod 2 1
           ........
~~~

## Author

* **Taekyoon Choi** - *10/31/17* - [Taekyoon](https://github.com/Taekyoon)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
