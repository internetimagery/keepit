// Testing utility functions!

package keepit

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
)

func TestExists(t *testing.T) {
	// Create temporary file and destroy
	wd, err := os.Getwd()
	if err != nil {
		t.Error(err)
	}
	temp_path := filepath.Join(wd, "tempfile.123")
	err = ioutil.WriteFile(temp_path, []byte("Here is some text!"), 600)
	if err != nil {
		t.Error(err)
	}
	defer os.Remove(temp_path)

	ok, err := Path_exists(temp_path)
	if err != nil {
		t.Error(err)
	}
	if !ok {
		t.Fail()
	}
}
