// Archive data in zip file

// TODO: Create index json file.

package keepit

import (
	"archive/zip"
	"errors"
	"io"
	"os"
)

func Store(path string, files map[string]string) error {
	if ok, err := path_exists(path); ok {
		if err != nil {
			return err
		}
		return errors.New("Archive already exists!")
	}

	newfile, err := os.Create(path)
	if err != nil {
		return err
	}
	defer newfile.Close()

	zipWriter := zip.NewWriter(newfile)
	defer zipWriter.Close()

	// Add files to zip
	for name, real_path := range files {

		zipfile, err := os.Open(real_path)
		if err != nil {
			return err
		}
		defer zipfile.Close()

		// Get the file information
		info, err := zipfile.Stat()
		if err != nil {
			return err
		}

		header, err := zip.FileInfoHeader(info)
		if err != nil {
			return err
		}

		// Change to deflate to gain better compression
		// see http://golang.org/pkg/archive/zip/#pkg-constants
		header.Method = zip.Deflate
		header.Name = name

		writer, err := zipWriter.CreateHeader(header)
		if err != nil {
			return err
		}
		_, err = io.Copy(writer, zipfile)
		if err != nil {
			return err
		}
	}
	return nil
}
