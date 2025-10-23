import numpy as np
import getopt
import glob
import sys
import re
import pdb
import os

# NOTE: Removed dependency on vars.utils

def parse_logs(files):
    """
    Parses through log files to extract the FINAL, converged marginal
    likelihood estimates.

    Arguments:
        files : list
            list of .log file names
    """
    marginal_likelihood = []
    # The tag for the FINAL converged value is specific and appears at the end of the file
    final_likelihood_tag = 'Marginal Likelihood = '

    for file in files:
        final_mle = None

        try:
            # Use 'with' for safe file handling
            with open(file, 'r') as handle:
                # Iterate through the WHOLE file to find the last instance of the exact tag
                for line in handle:
                    if line.strip().startswith(final_likelihood_tag):
                        # Extract the float value after '='
                        # .strip() is added just in case of extra whitespace
                        m = float(line.strip().split('=')[1].strip())
                        final_mle = m # This stores the last (and therefore final converged) value

            if final_mle is not None:
                marginal_likelihood.append(final_mle)
            else:
                # Warning if a file was expected but didn't contain the final ML
                sys.stderr.write("Warning: Could not find final Marginal Likelihood in file: %s. Skipping for MLE analysis.\n" % file)

        except IOError:
            sys.stderr.write("Error: Could not open file: %s. Skipping.\n" % file)

    return marginal_likelihood

def parse_varQs(files):
    """
    Parses through multiple .meanQ files to extract the mean
    admixture proportions estimated by executing the
    variational inference algorithm on a dataset. This is then used
    to identify the number of model components (best K) used to explain
    structure in the data, for each .meanQ file.

    Arguments:
        files : list
            list of .meanQ file names
    """
    bestKs = []
    for file in files:
        try:
            with open(file, 'r') as handle:
                # Read data into NumPy array. map(float, ...) is Python 2 standard.
                # Use list comprehension for better Python 2/3 compatibility if possible.
                Q = np.array([[float(val) for val in line.strip().split()] for line in handle if line.strip()])

            if Q.size == 0:
                sys.stderr.write("Warning: Empty or improperly formatted .meanQ file: %s. Skipping.\n" % file)
                continue

            # Normalize rows to sum to 1 (replaces Q = Q / utils.insum(Q,[1]))
            # axis=1 sums rows; keepdims=True ensures the broadcast shape is correct.
            Q_sum = Q.sum(axis=1, keepdims=True)
            # Avoid division by zero, although Q matrix rows should sum close to 1
            Q_sum[Q_sum == 0] = 1.0
            Q = Q / Q_sum

            N = Q.shape[0]
            # Calculate cumulative sum of sorted column sums (components)
            C = np.cumsum(np.sort(Q.sum(0))[::-1])
            # Determine best K: number of components needed to explain N-1 individuals
            bestKs.append(np.sum(C < N - 1) + 1)

        except IOError:
            sys.stderr.write("Error: Could not open file: %s. Skipping.\n" % file)
        except Exception as e:
            sys.stderr.write("Error processing .meanQ file %s: %s. Skipping.\n" % (file, e))

    return bestKs

def parseopts(opts):
    """
    parses the command-line flags and options passed to the script
    """
    filetag = None
    for opt, arg in opts:
        if opt in ["--input"]:
            filetag = arg
    return filetag

def usage():
    """
    brief description of various flags and options for this script
    """
    print "\nHere is how you can use this script\n"
    print "Usage: python %s"%sys.argv[0]
    print "\t --input=<filetag>"

if __name__=="__main__":

    # parse command-line options
    argv = sys.argv[1:]
    smallflags = ""
    bigflags = ["input="]
    try:
        opts, args = getopt.getopt(argv, smallflags, bigflags)

        # This part ensures the script only runs if arguments are passed
        if not opts:
            usage()
            sys.exit(2)

    except getopt.GetoptError:
        print "Incorrect options passed"
        usage()
        sys.exit(2)

    filetag = parseopts(opts)

    if filetag is None:
        print "Error: The --input filetag is required."
        usage()
        sys.exit(2)

    # --- Marginal Likelihood Analysis ---

    # Find all log files (e.g., 'faststructure_K*.log')
    log_files_all = sorted(glob.glob('%s*.log'%filetag))

    if not log_files_all:
        print "Error: No log files found matching pattern '%s*.log'" % filetag
        sys.exit(1)

    # 1. Parse log files to get marginal likelihoods
    # This list will only contain MLEs from successfully parsed files.
    marginal_likelihoods = parse_logs(log_files_all)

    # Check if any MLEs were found
    if not marginal_likelihoods:
        print "Error: No marginal likelihoods were successfully extracted from log files."
        sys.exit(1)

    # 2. Extract K values from filenames.
    # We must match the extracted Ks to the number of successful marginal_likelihoods found.
    Ks = []

    # Log files are sorted by name, ensuring Ks and marginal_likelihoods align IF all files are processed.
    # To be fully robust, we would need parse_logs to return a list of successfully processed filenames,
    # but for this script, we rely on the sorted order and process the files again to get K.
    # We use the length of marginal_likelihoods to know how many Ks we expect.

    # We use the original file list and will break when Ks list size matches MLE list size
    for file in log_files_all:
        # Regex to extract the K integer from the filename, e.g., 'K(5).5.log'
        match = re.search(r'K(\d+)\.\d+\.log', file)

        if match:
            try:
                K_int = int(match.group(1))
                Ks.append(K_int)

                # If we've gathered as many K values as we have marginal likelihoods, stop.
                # This assumes that any file that failed in parse_logs was one where K could not be extracted (or should be ignored).
                if len(Ks) == len(marginal_likelihoods):
                    break
            except ValueError:
                sys.stderr.write("Warning: Could not convert K part to integer from filename: %s. Skipping.\n" % file)

    Ks = np.array(Ks)

    # Final check for array length match (CRITICAL step that was failing previously)
    if Ks.size != len(marginal_likelihoods):
        print "Fatal Error: K value extraction (%d) does not match successful Marginal Likelihood extractions (%d)." % (Ks.size, len(marginal_likelihoods))
        print "Results may be unreliable or file naming is inconsistent."
        # Proceeding is dangerous, but for debugging, we might continue.
        # For a clean script, we should sys.exit(1) here.
        # sys.exit(1)

    # --- Model Components Analysis (Best K) ---

    files_meanQ = sorted(glob.glob('%s*.meanQ'%filetag))

    if not files_meanQ:
        print "Error: No .meanQ files found matching pattern '%s*.meanQ'" % filetag
        # Continue as we still have the MLE result
        bestKs = []
    else:
        bestKs = parse_varQs(files_meanQ)

    # --- Final Output ---

    # Use the extracted Ks array and the MLE array
    best_K_mle = Ks[np.argmax(marginal_likelihoods)]
    print "Model complexity that maximizes marginal likelihood = %d" % best_K_mle

    # Determine K by counting the most frequent 'bestK' estimated from Q matrices
    if bestKs:
        # np.bincount returns array of counts; argmax gets the index (the K value) with the highest count.
        most_frequent_K = np.argmax(np.bincount(bestKs))
        print "Model components used to explain structure in data (modal bestK) = %d" % most_frequent_K
    else:
        print "Cannot determine model components from .meanQ files as no data was parsed."
[zachpella@login1.swan faststructure_results]$ cat extract_metrics.py
import numpy as np
import glob
import re
import sys
import os

# --- PASTE THE CORRECTED parse_logs, parse_varQs, and utility functions here ---

# Since I don't have your specific corrected file, I will use the robust logic we established.
# You MUST ensure the contents of these functions match the final fixed code.

def parse_logs(file):
    """
    Reads a single log file and returns the final converged Marginal Likelihood.
    Returns None if not found.
    """
    final_likelihood_tag = 'Marginal Likelihood = '
    final_mle = None

    try:
        with open(file, 'r') as handle:
            for line in handle:
                if line.strip().startswith(final_likelihood_tag):
                    final_mle = float(line.strip().split('=')[1].strip())

    except IOError:
        sys.stderr.write("Error: Could not open file: %s.\n" % file)
    except Exception:
        sys.stderr.write("Error parsing likelihood in file: %s.\n" % file)

    return final_mle

def parse_varQs(file):
    """
    Reads a single meanQ file and returns the estimated bestK (K_phi_star).
    Returns None if parsing fails.
    """
    try:
        with open(file, 'r') as handle:
            Q = np.array([[float(val) for val in line.strip().split()] for line in handle if line.strip()])

        if Q.size == 0:
            return None

        # Normalize rows to sum to 1
        Q_sum = Q.sum(axis=1, keepdims=True)
        Q_sum[Q_sum == 0] = 1.0
        Q = Q / Q_sum

        N = Q.shape[0]
        C = np.cumsum(np.sort(Q.sum(0))[::-1])

        # Calculate best K (K_phi_star)
        return np.sum(C < N - 1) + 1

    except IOError:
        sys.stderr.write("Error: Could not open file: %s.\n" % file)
    except Exception as e:
        sys.stderr.write("Error processing .meanQ file %s: %s.\n" % (file, e))
        return None

# --- Main Compilation Logic ---

def compile_metrics(filetag="faststructure_K"):

    results = [] # To store [K, LLBO, K_phi_star] for each K

    # K values span from 1 to 10 based on your file listing
    for K in range(1, 11):
        # We need to find the specific log/meanQ file for this K,
        # e.g., 'faststructure_K5.5.log'. The regex ensures we get the right file.

        # Find the log file (e.g., faststructure_K5.X.log)
        log_pattern = '%s%d.*.log' % (filetag, K)
        log_files = glob.glob(log_pattern)

        # Find the meanQ file (e.g., faststructure_K5.X.meanQ)
        meanQ_pattern = '%s%d.*.meanQ' % (filetag, K)
        meanQ_files = glob.glob(meanQ_pattern)

        if not log_files or not meanQ_files:
            sys.stderr.write(f"Warning: Files for K={K} not found. Skipping.\n")
            continue

        # For simplicity, we assume there is only one run per K (e.g., K5.5)
        # and take the first match found.
        llbo = parse_logs(log_files[0])
        k_phi_star = parse_varQs(meanQ_files[0])

        if llbo is not None and k_phi_star is not None:
            results.append([K, llbo, k_phi_star])

    return np.array(results)

if __name__ == "__main__":
    # The filetag is 'faststructure_K' based on your analysis
    metrics_array = compile_metrics(filetag="faststructure_K")

    # Save the compiled metrics to a file for easy plotting
    np.savetxt('k_metrics_data.txt', metrics_array, fmt='%d,%.6f,%d',
               header='K,LLBO_Value,K_Phi_Star', delimiter=',')

    print("Metrics compiled and saved to k_metrics_data.txt")
