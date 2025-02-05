package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/spf13/cobra"
)

// Timestamps represents the structure of the JSON file
type Timestamps map[string]float64

func getModificationTimes(basePath string) (Timestamps, error) {
    modificationTimes := make(Timestamps)
    err := filepath.Walk(basePath, func(filePath string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }

        if !info.IsDir() {
            relPath, err := filepath.Rel(basePath, filePath)
            if err != nil {
                return err
            }
            modificationTimes[relPath] = float64(info.ModTime().Unix())
            fmt.Printf("VERBOSE: Traversed file: %s\n", filePath)
        }
        return nil
    })
    return modificationTimes, err
}

func setModificationTimes(path string, fileTimestamps Timestamps, verbose bool) error {
	existingTimes, err := getModificationTimes(path)
	if err != nil {
		return err
	}
	for filename, newTimestamp := range fileTimestamps {
		fullPath := filepath.Join(path, filename)
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			if verbose {
				fmt.Printf("VERBOSE: Skipping missing file: %s\n", fullPath)
			}
			continue
		}
		currentTimestamp, ok := existingTimes[filename]
		if ok && currentTimestamp == newTimestamp {
			if verbose {
				fmt.Printf("VERBOSE: Skipping unchanged file: %s\n", fullPath)
			}
			continue
		}

		newModTime := time.Unix(int64(newTimestamp), 0)


		fmt.Printf("Updating timestamp for: %s -> %f , %f\n", fullPath, newTimestamp, newModTime)
		// Uncomment to apply changes.  Be very careful with this!
        // if err := os.Chtimes(fullPath, newModTime, newModTime); err != nil {
		// 	return err
		// }



	}
	return nil
}

func main() {
	var outputFile string
	var inputFile string
	var verbose bool


	// dump command
	dumpCmd := &cobra.Command{
		Use:   "dump <path>",
		Short: "Dump file modification timestamps to a JSON file.",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			pathToTraverse := args[0]
            modificationTimes, err := getModificationTimes(pathToTraverse)
            if err != nil {
                return err
            }


			data, err := json.MarshalIndent(modificationTimes, "", "    ")
			if err != nil {
				return err
			}

			if err := os.WriteFile(outputFile, data, 0644); err != nil {
				return fmt.Errorf("failed to write to output file: %w", err)
			}
            fmt.Printf("File modification timestamps saved to %s\n", outputFile)
			return nil
		},
	}
    dumpCmd.Flags().StringVarP(&outputFile, "output", "o", "file_timestamps.json", "Output JSON file")

	// update command
	updateCmd := &cobra.Command{
		Use:   "update <path>",
		Short: "Update file modification times from a JSON file.",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			targetPath := args[0]

			// Load timestamps from JSON file
			data, err := os.ReadFile(inputFile)
			if err != nil {
				return fmt.Errorf("failed to read input file: %w", err)
			}

			var fileTimestamps Timestamps
			if err := json.Unmarshal(data, &fileTimestamps); err != nil {
				return fmt.Errorf("failed to parse JSON: %w", err)
			}

			return setModificationTimes(targetPath, fileTimestamps, verbose)
		},
	}
	updateCmd.Flags().StringVarP(&inputFile, "input", "i", "file_timestamps.json", "Input JSON file")
	updateCmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "Verbose logging")


	rootCmd := &cobra.Command{
		Use:   "fs_timestamp_tool",
		Short: "Tool to dump and update file modification timestamps.",
	}
	rootCmd.AddCommand(dumpCmd, updateCmd)


	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

}

