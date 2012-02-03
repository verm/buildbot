from struct import pack, unpack

from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor, defer

from twisted.conch.ssh.channel import SSHChannel
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.ssh.transport import SSHClientTransport, SSHTransportBase
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.userauth import SSHUserAuthClient
defer.setDebugging(True)


# BBClientTransport
class BBClientTransport(SSHClientTransport):
	def __init__(self, command, channel):
		self.command = command
		self.channel = channel
		self.sshslave = self.command.builder.sshslave

	def verifyHostKey(self, hostKey, fingerprint):

		if self.sshslave["fingerprint"] is None:
			pass
		elif fingerprint != self.sshslave["fingerprint"]:
			# Do something.
			pass

		print "Host fingerprint: %s" % fingerprint
		return defer.succeed(True)

	def connectionSecure(self):
		cc = BBSSHConnection(self.command, self.channel)
		auth = BBAuthClient(self.sshslave["login"], cc, self.command)
		self.requestService(auth)


# BBAuthClient
class BBAuthClient(SSHUserAuthClient):
	def __init__(self, user, cc, command):
		SSHUserAuthClient.__init__(self, user, cc)
		self.sshslave = command.builder.sshslave

	def getPublicKey(self):
		key = Key.fromFile(filename=self.sshslave["publicKey"])
		return key.blob()

	def getPrivateKey(self):
		key = Key.fromFile(self.sshslave["privateKey"])
		return defer.succeed(key.keyObject)


# BBSSHConnection
class BBSSHConnection(SSHConnection):
	def __init__(self, command, channel):
		SSHConnection.__init__(self)
		self.command = command
		self.channel = channel

	def serviceStarted(self):
		sshpool = self.command.builder.sshpool
		sshpool.add(self, self.command)

		self.openChannel(self.channel)


# BBSSHChannel
class BBSSHChannel(SSHChannel):
	name = 'session'

	def __init__(self, command, argv):
		SSHChannel.__init__(self)
		self.command = command
		self.argv = argv

	def openFailed(self, reason):
		self.command.deferred.errback(reason)

	def channelOpen(self, ignored):
		str_cmd = " ".join(self.argv)
		str_net = pack('!L', len(str_cmd)) + str_cmd
		self.conn.sendRequest(self, 'exec', str_net)

	def dataReceived(self, data):
		self.command.addStdout(data)

	def extReceived(self, data):
		self.command.addStderr(data)

	def closed(self):
		sig = None
		rc = 0
		self.command.finished(sig, rc)

	def request_exit_status(self, data):
		status = unpack('>L', data)[0]
		print "BBSSHChannel():request_exit_status(): %s" % status
#		self.loseConnection()
		self.command.builder.sshpool.free(self.command)

class SSHConnectionPool:
	pool = {}
	id_count = 0

	# Get a connection from the pool or return a new one.
	def _get(self, command, channel):
		sshslave = command.builder.sshslave
		name = sshslave["name"]

		for (i, x) in enumerate(self.pool.get(name, [])):
			if x["id"] is None:
				id = self.id_get()
				print "SSHConnectionPool:get(): reusing connection, new id: %s" % id
				self.pool[name][i]["id"] = id
				command.builder.sshpool_id = id

				return self.pool[name][i]["conn"].openChannel(channel)

		p = ClientCreator(reactor, BBClientTransport, command, channel)
		d = p.connectTCP(
			sshslave["host"],
			sshslave["port"],
			timeout=sshslave["timeout"],
			bindAddress=sshslave["bindAddress"])

		# XXX: If sshpool.workdir != workdir insert a deferred to change the directory.
		return d

	# Run a command
	def run(self, command, argv):
		channel = BBSSHChannel(command, argv)
		return self._get(command, channel)


	def add(self, conn, command):
		builder = command.builder
		name = builder.sshslave["name"]
		builder.sshpool_id = self.id_get()

		new = {
			"id": builder.sshpool_id,
			"conn" : conn,
			"workdir": command.workdir,
		}

		self.pool.setdefault(name, []).append(new)
		print "SSHConnectionPool:add(): new connection: %s" % new


	def free(self, command):
		id = command.builder.sshpool_id
		name = command.builder.sshslave["name"]

		print "SSHConnectionPool:remove(): free connection %s" % id

		for (i, x) in enumerate(self.pool[name]):
			if x["id"] == id: 
				self.pool[name][i]["id"] = None


	def id_get(self):
		# locking disaster?
		self.id_count += 1
		return self.id_count
