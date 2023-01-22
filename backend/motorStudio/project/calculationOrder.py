class calculationOrder(object):
    """ Contains the details about the calculation order. The data is mainly used for the report generation. """

    def __init__(self):
        self.costAccount = 'DP, IA or Cost center'
        self.dateOfReceipt = 'TBD'
        self.deadline = 'TBD'
        self.productDesignLevel = 'Prototype'
        self.articelNumber = '1.XX.XXX.XXX'
        self.projectNumber = 'e.g. SP IP'
        self.orderer = 'Bühler Motor GmbH'
        self.customer = None
        self.projectName = 'Test'
        self.variationName = 'Var%03d0' % 1
        self.userName = 'Marko Markovic'

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            'User Name':self.userName,
            'Orderer':self.orderer,
            'Project Name':self.projectName,
            'Customer':self.customer,
            'Cost Account':self.costAccount,
            'Article Number':self.articelNumber,
            'Date of Receipt':self.dateOfReceipt,
            'Deadline':self.deadline,
            'Product Design Level':self.productDesignLevel,
        }
