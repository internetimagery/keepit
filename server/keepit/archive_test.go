// Testing archive

package keepit

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
)

func TestArchive(t *testing.T) {
	// Setup
	wd, err := os.Getwd()
	tmp_dir := filepath.Join(wd, "temp")
	if ok, err := exists(tmp_dir); !ok {
		if err != nil {
			t.Error(err)
		}
		os.Remove(tmp_dir)
	}
	err = os.Mkdir(tmp_dir, 700)
	defer os.Remove(tmp_dir)
	if err != nil {
		t.Error(err)
	}

	if err != nil {
		t.Error(err)
	}
	test_file := filepath.Join(tmp_dir, "testfile")
	ioutil.WriteFile(test_file, []byte("Some information here!"), 700)
	index := map[string]string{
		"testfile": test_file,
	}

	t.Run("Create", func(t *testing.T) {
		path := filepath.Join(tmp_dir, "create_test.zip")
		err := Store(path, index)
		if err != nil {
			t.Error(err)
		}
		if ok, _ := exists(path); !ok {
			t.Fail()
		}
	})
}
