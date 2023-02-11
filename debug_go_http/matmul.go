package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"strconv"
	"time"

	"gonum.org/v1/gonum/mat"
)

type Message struct {
	N string 
  }
func matmul() {
	req_str := "{\"n\":\"100\"}"
	bytes := []byte(req_str)
	// fmt.Println(string(bytes))
	var m = Message{}

	err := json.Unmarshal(bytes, &m)
	if err != nil {
		panic(err)
	}
	// if err := json.Unmarshal(req, &dat); err != nil {
    //     return "invalid request!\n"
    // }
	// fmt.Println(dat)
	// n_str := dat["n"].(string)
	// // var var_1 string = n_str
	// // var n_int int = n_str
	// fmt.Printf("type of n is: %T\n", m.n)
	fmt.Println(m)
	n , _ := strconv.Atoi(m.N)
	// fmt.Println(n)

	// n := 10000
	a := make([]float64, n*n)
	b := a
	for i := range a {
		a[i] = rand.Float64()
		b[i] = rand.Float64()
	}
	// fmt.Println(data)
	a_mat := mat.NewDense(n, n, a)
	b_mat := mat.NewDense(n, n, b)
	
	// b := mat.NewDense(n, n, []float64{
	// 	1, 2,
	// 	3, 4,
	// })

	// Take the matrix product of a and b and place the result in c.
	var c mat.Dense
	start := time.Now()

	c.Mul(a_mat, b_mat)
	// Code to measure
	duration := time.Since(start)

	// Formatted string, such as "2h3m0.5s" or "4.503μs"
	fmt.Println(duration.Seconds())

	// Print the result using the formatter.
	// fc := mat.Formatted(&c, mat.Prefix("    "), mat.Squeeze())
	// fmt.Printf("c = %v", fc) 

}