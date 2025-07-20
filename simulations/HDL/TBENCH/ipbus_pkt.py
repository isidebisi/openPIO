##  Author: Delphine Allimann
##  EPFL - TCL 2025

# Documentation about IPbus protocol : https://ipbus.web.cern.ch/doc/user/html/_downloads/d251e03ea4badd71f62cffb24f110cfa/ipbus_protocol_v2_0.pdf

class IpbusPkt:

    def __init__(self,tb):
        self.header = [0xf0,0x00,0x00,0x20]
        self.transactions = [] #list of IpbusTransaction objects 
        self.tb = tb
    
    def add_transactions(self, transactions=[]):
        self.transactions += transactions
        return

    def get_pkt(self):
        pkt = []
        pkt += self.header
        for each in self.transactions : 
            pkt += each.get_transaction()
        return pkt
    
    def construct_pkt(self, raw):
        raw = list(raw)
        self.header = raw[0:4]
        start_index = 4

        while start_index < len(raw):
            transaction = IpbusTransaction(self.tb)
            start_index += transaction.construct_transaction(raw[start_index:])
            self.transactions.append(transaction)
            
        return
    
    def print_pkt(self):
        nbr_transactions = len(self.transactions)
        string = ""
        if (nbr_transactions > 1):
            string = "s"
        self.tb.log.info("This IPbus packet contains %s transaction%s : ", len(self.transactions), string)
        for each in self.transactions:
            each.print_clean()
        return



class IpbusTransaction:

    def __init__(self, tb, id=0):
        self.tb     = tb
        self.header = []
        self.addr   = []
        self.data   = []
        self.id     = id
        self.type   = ""

        self.info_code = 0
        self.nbr_words = 0
        
    def get_transaction(self):
        return self.header + self.addr + self.data

    def build_write(self, nbr_words=2, addr=[0x00,0x10,0x00,0x00], data=[x for x in range(64)]):
        self.header = [0x1f,nbr_words,self.id,0x20]
        self.addr = addr
        self.data = data
        self.type = "write request"
        self.info_code = 0xf
        self.nbr_words = nbr_words
        return 

    def build_read(self, nbr_words=2, addr=[0x00,0x10,0x00,0x00]):
        self.header = [0x0f,nbr_words,self.id,0x20]
        self.addr   = addr
        self.type = "read request"
        self.info_code = 0xf
        self.nbr_words = nbr_words
        return 
    
    def print_clean(self):
        id_str   = "Id = " + str(self.id) + " : " + str(self.type)
        word_str = "of " + str(self.nbr_words) + " words"
        addr_str = "at the address " + str(self.addr)
        data_str = ", Data : " + str(bytes(self.data))

        if(self.type == "read request"):
            self.tb.log.info("%s %s %s", id_str, word_str, addr_str)

        elif(self.type == "read response"):
            self.tb.log.info("%s %s %s", id_str, word_str, data_str)

        elif(self.type == "write request"):
            self.tb.log.info("%s %s %s %s", id_str, word_str, addr_str, data_str)

        else: self.tb.log.info("%s", id_str)    

        return
    
    def construct_transaction(self, raw):
        
        self.header = raw[0:4]
        self.nbr_words = self.header[1]
        self.id = self.header[2]
        type_code = self.header[0]

        if (type_code == 0x0f):  
            self.type = "read request"
            self.info_code = 0xf
            self.addr = raw[4:8]
            end_index = 8
            return end_index

        if (type_code == 0x00):  
            self.type = "read response"
            self.info_code = 0x0
            end_index = 4+self.nbr_words*4
            self.data = raw[4:end_index]
            return end_index

        if (type_code == 0x10):  
            self.type = "write ack"
            self.info_code = 0x0
            end_index = 4
            return end_index

        if (type_code == 0x1f): 
            self.type = "write request"
            self.info_code = 0xf
            self.addr = raw[4:8]
            end_index = 8+self.nbr_words*4
            self.data = raw[8:end_index]
            return end_index
        
        if (type_code == 0x06): 
            self.type = "bus timeout on read"
            end_index = 4
            return end_index
        
        if (type_code == 0x17): 
            self.type = "bus timeout on write"
            end_index = 4
            return end_index

        if (type_code == 0x04): 
            self.type = "bus error on read"
            end_index = 4
            return end_index

        if (type_code == 0x05): 
            self.type = "bus error on write"
            end_index = 4
            return end_index
    
        self.tb.log.info("non identified packet, header = %s - skipped", bytes(self.header))
        end_index = 4
        return end_index
    
    def print_test(self):
        self.tb.log.info("type is %s, addr is %s, id is %s, data is %s and nbr of words is %s", self.type, self.addr, self.id, bytes(self.data), self.nbr_words)
        self.tb.log.info("header is %s, addr is %s", list(self.header), self.addr)