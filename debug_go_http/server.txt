package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func main() {
    http.HandleFunc("/hello", func(w http.ResponseWriter, r *http.Request) {
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
            fmt.Println("Error reading request body:", err)
            http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            return
        }
		fmt.Fprintf(w, "Request body received\n")
		fmt.Println(string(body))
		w.Write(body)
    })

	http.HandleFunc("/callback", func(w http.ResponseWriter, r *http.Request) {
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
            fmt.Println("Error reading request body:", err)
            http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            return
        }
		fmt.Fprintf(w, "Request body received\n")
		fmt.Println(string(body))
		w.Write(body)
		//write to file
		file, err := os.Create("./output.txt")

		if err != nil {
			fmt.Println(err)
			return
		}
		defer file.Close()
	
		// write the string to the file
		_, err = file.WriteString(string(body))
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Println("File written successfully.")
    })

    http.ListenAndServe(":8000", nil)

	// var err error

	// message := fmt.Sprintf("Body: %s", string(req.Body))
	// fmt.Printf(message, "\n")
	// return handler.Response{
	// 	Body:       []byte(message),
	// 	StatusCode: http.StatusOK,
	// }, err
}
