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
	wd, _ := os.Getwd()
	tmp_dir := filepath.Join(wd, "temp")
	os.Mkdir(tmp_dir, 700)
	defer os.Remove(tmp_dir)

	// Create a test file to archive
	test_file := filepath.Join(tmp_dir, "testfile.file")
	arch_file := filepath.Join(tmp_dir, "archive.zip")
	ioutil.WriteFile(test_file, []byte("Some information here!"), 700)
	index := map[string]string{
		"testfile": test_file,
	}

	// Run tests
	t.Run("Create", func(t *testing.T) {
		err := Store(arch_file, index)
		if err != nil {
			t.Error(err)
		}
		if ok, _ := path_exists(arch_file); !ok {
			t.Fail()
		}
	})
	t.Run("Read Only", func(t *testing.T) {
		err := Store(arch_file, index)
		if err == nil {
			t.Fail()
		}
	})
	t.Run("Recover", func(t *testing.T) {

	})
}
