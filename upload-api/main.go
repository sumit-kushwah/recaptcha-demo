package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/joho/godotenv"
)

func verifyRecaptcha(token string, captchaType string, remoteIp string) bool {
	if token == "" {
		return false
	}
	captchaType = strings.ToUpper(captchaType)
	envVariable := captchaType + "_SECRET_KEY"
	secret_key := os.Getenv(envVariable)
	formData := url.Values{}
	formData.Add("secret", secret_key)
	formData.Add("response", token)
	formData.Add("remoteip", remoteIp)

	resp, err := http.PostForm("https://www.google.com/recaptcha/api/siteverify", formData)
	if err != nil {
		return false
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		return false
	}

	responseData := make(map[string]interface{})
	if err := json.Unmarshal(body, &responseData); err != nil {
		return false
	}

	if result, ok := responseData["success"].(bool); ok {
		return result
	}
	return false
}

var healthCheck = func(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"code":    http.StatusOK,
		"error":   nil,
		"data":    nil,
		"message": "Upload file api is up and running!",
	})
}

var fileUpload = func(c *gin.Context) {
	// Parse the form data
	err := c.Request.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"code":    http.StatusBadRequest,
			"error":   err.Error(),
			"data":    nil,
			"message": "Failed to parse form data",
		})
		return
	}

	// Before uploading the file, verify the recaptcha
	token := c.Request.FormValue("g-recaptcha-response")
	captchaType := c.Request.FormValue("captcha_type")
	remoteIp := c.ClientIP()

	if !verifyRecaptcha(token, captchaType, remoteIp) {
		c.JSON(http.StatusBadRequest, gin.H{
			"code":    http.StatusBadRequest,
			"error":   "Invalid token to upload file",
			"data":    nil,
			"message": "Spam detected!",
		})
		return
	}

	// Get the form data
	file, header, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"code":    http.StatusBadRequest,
			"error":   err.Error(),
			"data":    nil,
			"message": "Failed to get file data",
		})
		return
	}
	defer file.Close()
	// unique id generator
	id := uuid.New().String() + "_"
	fileName := "uploads/" + id + header.Filename
	out, err := os.Create(fileName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"code":    http.StatusInternalServerError,
			"error":   err.Error(),
			"data":    nil,
			"message": "failed to create file",
		})
		return
	}
	defer out.Close()
	_, err = io.Copy(out, file)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"code":    http.StatusInternalServerError,
			"error":   err.Error(),
			"data":    nil,
			"message": "failed to write file",
		})
		return
	}

	// Return success response
	c.JSON(http.StatusOK, gin.H{
		"code":    http.StatusOK,
		"message": "File uploaded successfully",
		"error":   nil,
		"data": map[string]string{
			"file_url": "http://" + c.Request.Host + "/" + fileName,
		},
	})
}

var cleanUp = func(c *gin.Context) {
	// clean up the uploaded file
	dir := "./uploads"
	d, err := os.Open(dir)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"code":    http.StatusInternalServerError,
			"error":   err.Error(),
			"data":    nil,
			"message": "Failed to open directory",
		})
		return
	}
	defer d.Close()

	names, err := d.Readdirnames(-1)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"code":    http.StatusInternalServerError,
			"error":   err.Error(),
			"data":    nil,
			"message": "Failed to read directory names",
		})
		return
	}

	deleteCount := 0
	for _, name := range names {
		err = os.RemoveAll(filepath.Join(dir, name))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"code":    http.StatusInternalServerError,
				"error":   err.Error(),
				"data":    nil,
				"message": "Failed to remove file",
			})
			return
		}
		deleteCount++
	}
	c.JSON(http.StatusOK, gin.H{
		"code":  http.StatusOK,
		"error": nil,
		"data": map[string]interface{}{
			"deleted_files_count": deleteCount,
		},
		"message": "Cleanup successful",
	})
}

func NewRouter() *gin.Engine {
	router := gin.Default()
	// disable cors for all origins
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})
	router.Static("/uploads", "./uploads")
	api := router.Group("/api")
	api.GET("", healthCheck)
	api.GET("/", healthCheck)
	api.POST("/upload", fileUpload)
	api.DELETE("/cleanup", cleanUp)
	return router
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	gin.SetMode(gin.ReleaseMode)
	router := NewRouter()
	fmt.Println("Starting server on port 3001")
	router.Run(":3001")
}
