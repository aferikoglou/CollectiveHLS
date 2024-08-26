import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class Preprocessor:
    """
    Handles the standardization and PCA of source code feature vectors
    in the application dataset.
    """

    def __init__(self, pc_num):
        """
        Initializes the Preprocessor with the specified number of principal components.

        Args:
            pc_num (int): Number of principal components to retain during PCA.
        """
        self.APP_SOURCE_CODE_CHARACTERISTICS_DATASET = "./KnowledgeBase/Source-Code-Feature-Vectors.csv"
        self.pc_num = pc_num

    def _standardize_data(self, X):
        """
        Standardizes the input data to have zero mean and unit variance.

        Args:
            X (numpy.ndarray): The input data to be standardized.

        Returns:
            numpy.ndarray: The standardized data.
        """
        standard_scaler = StandardScaler()
        return standard_scaler.fit_transform(X)

    def _pca(self, X):
        """
        Applies Principal Component Analysis (PCA) to reduce the dimensionality of the input data.

        Args:
            X (numpy.ndarray): The standardized input data.

        Returns:
            numpy.ndarray: The data transformed by PCA.
        """
        pca = PCA(n_components=self.pc_num)
        return pca.fit_transform(X)

    def preprocess(self):
        """
        Reads the dataset, standardizes the data, applies PCA, and returns the results as a DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame containing the principal components and application names.
        """
        # Read the dataset containing application names and feature vectors
        df = pd.read_csv(self.APP_SOURCE_CODE_CHARACTERISTICS_DATASET)
        app_names = df['Application_Name'].to_numpy()
        
        # Drop the 'Application_Name' column and convert the remaining data to a NumPy array
        df_values = df.drop(columns="Application_Name").to_numpy()

        # Standardize the feature vectors
        standardized_input = self._standardize_data(df_values)

        # Apply PCA to reduce dimensionality
        scores = self._pca(standardized_input)

        # Create a DataFrame with the principal components and the corresponding application names
        df_pca = pd.DataFrame(scores, columns=[f'PC{i}' for i in range(1, self.pc_num + 1)])
        df_pca["Application_Name"] = app_names

        return df_pca
