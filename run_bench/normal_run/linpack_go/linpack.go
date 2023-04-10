package main

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"

	"gonum.org/v1/gonum/mat"
)

type Message struct {
	N string
}

// Handle a serverless request
func main() {
	// var m Message
	// err := json.Unmarshal(req, &m)
	// if err != nil {
	// 	// return fmt.Sprintf("Invalide input!!\n")
	// }
	n, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Printf("Invalide input!!\n")
	}

	exec_time := linpack(n)
	fmt.Printf("%.2f\n", exec_time)
}

func linpack(n int) float64 {
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
		return 0
	}
	duration := time.Since(start)
	// fmt.Println(duration.Seconds())

	return duration.Seconds()
}
