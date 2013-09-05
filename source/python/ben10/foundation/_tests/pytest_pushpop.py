from ben10.foundation.pushpop import PushPop



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testPushPop(self):

        class MyObject:

            class_value = 1

            def __init__(self, value):
                self.value = value

        obj = MyObject(1)

        assert obj.value == 1
        with PushPop(obj, 'value', 2) as value:
            assert obj.value == 2
            assert value == 2
        assert obj.value == 1

        assert MyObject.class_value == 1
        assert obj.class_value == 1
        with PushPop(MyObject, 'class_value', 2) as value:
            assert MyObject.class_value == 2
            assert obj.class_value == 2
            assert value == 2
        assert MyObject.class_value == 1
        assert obj.class_value == 1
