package main

import (
	// "github.com/gonum/matrix/mat64"
	"fmt"
	"math/rand"
	"time"

	"gonum.org/v1/gonum/mat"
)

func main() {
	var n = 1000

	a := make([]float64, n*n)
	b := make([]float64, n*n)
	for i := range a {
		a[i] = rand.Float64()
		b[i] = rand.Float64()
	}

	a_mat := mat.NewDense(n, n, a)
	b_mat := mat.NewDense(n, n, b)
	start := time.Now()
	err := b_mat.Solve(b_mat, a_mat)
	if err != nil {
		fmt.Println("error\n")
		return 
	}
	duration := time.Since(start)
	fmt.Println(duration.Seconds())
}