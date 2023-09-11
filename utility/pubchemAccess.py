import pubchempy as pcp

#https://pubchempy.readthedocs.io/en/latest/guide/introduction.html

class pubchem:

    def searchCompoundName(self, name):
        c = pcp.get_compounds(name, 'name')
        self.parseCompound(c)

    def searchCompoundSmiles(self, smiles):
        c = pcp.get_compounds(smiles, 'smiles')
        self.parseCompound(c)

    def parseCompound(self, compounds):
        for compound in compounds:
            print(compound.molecular_formula)
            print(compound.isomeric_smiles)



if __name__ == '__main__':
    test = pubchem()
    test.searchCompoundSmiles('Cn1c2cccc3c2[C+]2c4c1cccc4oc1c2c(o3)ccc1')