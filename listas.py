from datetime import datetime

class Cliente:
    def __init__(self):
        self.cliente = []
        self.contadorCliente = 0
        self.contadorClienteActualizar = 0
    
    def agregar_cliente(self, nit, nombre):
        self.cliente.append([nit, nombre])
        self.contadorCliente += 1
        return self.cliente
    

    def actualizar_cliente(self, nit, nombre):
        
        for i in range(len(self.cliente)):
            if self.cliente[i][0] == nit:
                self.cliente[i][1] = nombre
                self.contadorClienteActualizar += 1
                return True
                
        return False
    
    def getNombreCliente(self, nit):
        for i in range(len(self.cliente)):
            if self.cliente[i][0] == nit:
                return self.cliente[i][1] #retorna el nombre
        return 'Cliente nombre no encontrado'
    
    def getNitCliente(self, nit):
        for i in range(len(self.cliente)):
            if self.cliente[i][0] == nit:
                return self.cliente[i][0] #retorna el nit
        return 'Cliente nit no encontrado'
    
    def limpiar(self):
        self.cliente = []
        self.contadorCliente = 0
        self.contadorClienteActualizar = 0

class Bancos:
    
    def __init__(self):
        self.bancos = []
        self.contadorbancos = 0
        self.contadorBancoActualizados = 0

    
    def agregar_banco(self, codigo, nombre):
        self.bancos.append([codigo, nombre])
        self.contadorbancos += 1
        return self.bancos
    
    def actualizar_banco(self, codigo:int, nombre):
        for i in range(len(self.bancos)):
            if self.bancos[i][0] == codigo:
                self.bancos[i][1] = nombre
                self.contadorBancoActualizados += 1
                return True
                
        return False
    
    


    def getCodBanco(self, codigo):
        for i in range(len(self.bancos)):
            if self.bancos[i][0] == codigo:
                return self.bancos[i][0] #retorna el codigo
        return 'Banco no encontrado'
    
    def getNombreBanco(self, codigo):
        for i in range(len(self.bancos)):
            if self.bancos[i][0] == codigo:
                return self.bancos[i][1] #retorna el nombre
        return 'Banco no encontrado'
    
    
    def limpiar(self):
        self.bancos = []
        self.contadorbancos = 0
        self.contadorBancoActualizados = 0

class facturas(Cliente):
    def __init__(self):
        Cliente.__init__(self)
        self.facturas = []
        self.contadorFactura = 0
        self.duplicadaFactura = 0
        self.FacturaError = 0
        self.monto = 0

    def agregar_factura(self, numFactura, nitCliente, fecha, valor):
        self.facturas.append([numFactura, nitCliente, fecha, valor])
        self.contadorFactura += 1
        lista_ordenada = sorted(self.facturas, key=lambda x: self.convertir_fecha(x[2]),  reverse=True)
        self.facturas = lista_ordenada
        return self.facturas
    
    def factura_duplicada(self, numFactura):
        for i in range(len(self.facturas)):
            if self.facturas[i][0] == numFactura:
                self.duplicadaFactura += 1
                return True
        return False
    

    def getFacturaSegunNitCliente(self, nit):
        listaTempo = []
        for i in range(len(self.facturas)):
            if self.facturas[i][1] == nit:
                listaTempo.append(self.facturas[i])
        if len(listaTempo) > 0:
            return listaTempo #retorna la factura
         
        return 'Factura no encontrada'
        
    def convertir_fecha(self,fecha_str):
        return datetime.strptime(fecha_str, '%d/%m/%Y')

    # def ordenarFacturas(self):
    #     self.convertir_fecha(self.facturas[2])
    
    def montoFacturasNitCliente(self, nitCliente):
        self.monto = 0
        for i in range(len(self.facturas)):
            if self.facturas[i][1] == nitCliente:
                self.monto += self.facturas[i][3]
        return self.monto
    

    def limpiar(self):
        self.facturas = []
        self.contadorFactura = 0
        self.duplicadaFactura = 0
        self.FacturaError = 0
        self.monto = 0


class pagos(Cliente, Bancos):
    def __init__(self):
        Cliente.__init__(self)
        Bancos.__init__(self)
        self.pagos = []
        self.contadorPago = 0
        self.duplicadoPago = 0
        self.pagoError = 0
        self.montoPago= 0
        

    # def copiaLista(self):
    #     return self.pagos.copy()

    def agregar_pago(self, codBanco, fecha, nitCliente, valor):
        self.pagos.append([codBanco, fecha, nitCliente, valor])
        self.contadorPago += 1
        litaTempo = sorted(self.pagos, key=lambda x: self.convertir_fecha(x[1]),  reverse=True)
        self.pagos = litaTempo
        
        return self.pagos
    
    def pago_duplicado(self, codBanco:int, nit, fecha):
        for i in range(len(self.pagos)):
            if self.pagos[i][0] == codBanco and self.pagos[i][2] == nit and self.pagos[i][1] == fecha:
                self.duplicadoPago += 1
                return True
        return False
    
    def getPagosSegunNitCliente(self, nitCliente):
        listaTempo = []
        for i in range(len(self.pagos)):
            if self.pagos[i][2] == nitCliente:
                listaTempo.append(self.pagos[i])

        if len(listaTempo) > 0:
            return listaTempo
        return 'Pago no encontrado'     

    def convertir_fecha(self,fecha_str):
        return datetime.strptime(fecha_str, '%d/%m/%Y')


    def montoPagosNitCliente(self, nitCliente):
        self.montoPago = 0
        for i in range(len(self.pagos)):
            if self.pagos[i][2] == nitCliente:
                self.montoPago += self.pagos[i][3]
        return self.montoPago

    def limpiar(self):
        self.pagos = []
        self.contadorPago = 0
        self.duplicadoPago = 0
        self.pagoError = 0
        self.montoPago = 0
        


      