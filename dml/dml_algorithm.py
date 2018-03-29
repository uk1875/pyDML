""" 
Distance Metric Algorithm.

Abstract class representing a Distance Metric Learning algorithm.
"""

from numpy.linalg import cholesky
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array
from sklearn.metrics.pairwise import pairwise_kernels
from .dml_utils import metric_to_linear

class DML_Algorithm(BaseEstimator,TransformerMixin):


    def __init__(self):
        	raise NotImplementedError('Class DML_Algorithm is abstract and cannot be instantiated.')


    # A DML Algorithm can compute either a Mahalanobis metric matrix or an associated linear transformation.
    # DML subclasses must override one of the following methods (metric or transformer), according to their computatoin way.
    def metric(self):
        """Computes the Mahalanobis matrix from the transformation matrix.
        .. math:: M = L^{\\top} L
    
        Returns
        -------
        M : (d x d) matrix
        """
        if hasattr(self,'M_'):
            return self.M_
        else:
            if hasattr(self,'L_'):
                L = self.transformer()
                self.M_ = L.T.dot(L)
                return self.M_
            else:
                raise NameError("Metric was not defined. Algorithm was not fitted.")

    def transformer(self):
        """Computes the transformation matrix from the Mahalanobis matrix.
    
        L = inv(cholesky(M))
    
        Returns
        -------
        L : (d x d) matrix
        """
        
        if hasattr(self,'L_'):
            return self.L_
        else:
            if hasattr(self,'M_'):
                try:
                    L = cholesky(self.metric()).T
                    return L
                except:
                    L = metric_to_linear(self.metric())
                    return L
                self.L_ = L
                return L
            else:
                raise NameError("Transformer was not defined. Algorithm was not fitted.")
    
    def transform(self, X=None):
        """Applies the metric transformation.
    
        Parameters
        ----------
        X : (n x d) matrix, optional
            Data to transform. If not supplied, the training data will be used.
    
        Returns
        -------
        transformed : (n x d) matrix
            Input data transformed to the metric space by :math:`XL^{\\top}`
        """
        if X is None:
            X = self.X_
        else:
            X = check_array(X, accept_sparse=True)
        L = self.transformer()
        return X.dot(L.T)
    
    def metadata(self):
        return {}
    
class KernelDML_Algorithm(DML_Algorithm):
    def __init__(self):
        	raise NotImplementedError('Class KernelDML_Algorithm is abstract and cannot be instantiated.')
            

    def _get_kernel(self,X,Y=None):
        if callable(self.kernel_):
            params = self.kernel_params_ or {}
        else:
            params = {'gamma':self.gamma_,
                      'degree':self.degree_,
                      'coef0':self.coef0_}
            
        return pairwise_kernels(X,Y,metric=self.kernel_,filter_params=True,**params)
    
    @property
    def _pairwise(self):
        return self.kernel_ == "precomputed"
    
    def transform(self,X=None):
        if X is None:
            X=self.X_
        else:
            X=check_array(X,accept_sparse=True)
            
        L=self.transformer()
        K=self._get_kernel(X,self.X_)
        return K.dot(L.T)
